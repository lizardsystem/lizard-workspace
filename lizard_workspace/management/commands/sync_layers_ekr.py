import json
import logging

from django.db import transaction
from django.utils import simplejson
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from optparse import make_option

from lizard_workspace.models import Layer
from lizard_workspace.models import Tag

from copy import deepcopy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ("""
Use a Layer template and some hardcoded criteria to create new Layers for ekr scores

prerequisites
- a Layer as a template

The default is called "vss_area_value", because querying our
/layers/wms (using sync_layers_with_wmsservers) returns a
vss:vss_area_value entry.

Example: bin/django sync_layers_ekr --slug=<slug of existing Layer>
""")

    option_list = BaseCommand.option_list + (
        make_option('--slug',
                    help='slug of existing Layer',
                    type='str',
                    default='vss_area_value'),)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        logger.info('start sync')
        slug = options['slug']
        source_ident = 'lizard-layers::%s' % slug

        layer = Layer.objects.get(slug=slug)
        original_tags = layer.tags.all()
        logger.info('template: %s' % layer)

        tag, _ = Tag.objects.get_or_create(slug=slug)
        logger.info('tag: %s' % tag)

        logger.debug('Invalidating existing layers...')
        existing_layers = dict(
            (l.slug, l) for l in
            Layer.objects.filter(source_ident=source_ident))
        for existing_layer in existing_layers.values():
            # Invalidate first and remove tags
            existing_layer.valid = False
            existing_layer.tags.clear()
            existing_layer.save()

        count_update, count_new = 0, 0
        
        group_tag = 'ekr-layers'
        name_cql_style = (
            ('EKR VIS', "name = 'EKR-VIS'", 'vss_ekr_value'),
            ('EKR FYTOPL', "name = 'EKR-FYTOPL'", 'vss_ekr_value'),
            ('EKR MAFAUNA', "name = 'EKR-MAFAUNA'", 'vss_ekr_value'),
            ('EKR OVWFLORA', "name = 'EKR-OVWFLORA'", 'vss_ekr_value'),
            ('EKR Minst gunstig', "name = 'EKR-ONGUNSTIG'", 'vss_ekr_value'),
            ('EKR Doelstelling', "name = 'EKR-DOELSCORE'", 'vss_ekr_score'),
        )
        for name, cql, style in name_cql_style:

            instance_slug = slugify(name)
            if instance_slug in existing_layers:
                # Update existing, the old existing tags have been
                # removed already.
                new_layer = existing_layers[instance_slug]
                logger.debug('Update: %s' % instance_slug)
                new_layer.data_set = layer.data_set
                count_update += 1
            else:
                # New
                logger.debug('New: %s' % instance_slug)
                new_layer = deepcopy(layer)
                new_layer.slug = instance_slug
                new_layer.id = None
                count_new += 1

            layer_params = []
            new_layer.filter = cql

            # Note that the same name can occur multiple times, but
            # with different mod, qua and/or stp.
            new_layer.name = name
            new_layer.source_ident = source_ident
            new_layer.valid = True
            new_layer.is_local_server = True
            new_layer.is_clickable = layer.is_local_server
            new_layer.js_popup_class = layer.js_popup_class
            new_layer.request_params = simplejson.dumps(dict(styles=style))
            new_layer.save()

            new_layer.tags.add(tag)
            for original_tag in original_tags:
                new_layer.tags.add(original_tag)
            group_tag, _ = Tag.objects.get_or_create(
                slug=group_tag,
            )
            new_layer.tags.add(group_tag)

        logger.info('new %d items' % count_new)
        logger.info('updated %d items' % count_update)
