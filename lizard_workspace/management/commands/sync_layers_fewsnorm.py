import json
import logging

from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from lizard_workspace.models import Layer
from lizard_workspace.models import Tag

from lizard_fewsnorm.models import TimeSeriesCache

from copy import deepcopy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ("""
Use a Layer template and fewsnorm to create new Layers for fewsnorm
(params, qualifiersets). All the properties and tags will be reset.

Prerequisities:
- a Layer as a template
- filled fewsnorm cache using sync_fewsnorm

The default is called "fews_locations", because querying our
/layers/wms (using sync_layers_with_wmsservers) returns a
vss:fews_locations entry.

Example: bin/django sync_layers_fewsnorm --slug=<slug of existing Layer>
""")

    option_list = BaseCommand.option_list + (
        make_option('--slug',
                    help='slug of existing Layer',
                    type='str',
                    default='vss_fews_locations'),)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        logger.info('start sync')
        slug = options['slug']
        source_ident = 'fewsnorm::%s' % slug

        layer = Layer.objects.get(slug=slug)
        original_tags = layer.tags.all()
        logger.info('template: %s' % layer)

        tag, _ = Tag.objects.get_or_create(slug='fewsnorm_%s' % slug)
        logger.info('tag: %s' % tag)

        logger.debug('Invalidating existing layers...')
        existing_layers = dict(
            (l.slug, l) for l in
            Layer.objects.filter(source_ident=source_ident))
        for existing_layer in existing_layers.values():
            # Invalidate first.
            existing_layer.valid = False
            # Remove tags from many to many relationships, not delete
            # the tags themselves.
            for layer_tag in existing_layer.tags.all():
                existing_layer.tags.remove(layer_tag)
            existing_layer.save()

        count_update, count_new = 0, 0

        for par_mod_qua_stp in TimeSeriesCache.objects.filter(active=True).values(
            "parametercache__ident", "parametercache__name", "modulecache__ident",
            "qualifiersetcache__ident", "timestepcache__ident").distinct():
            par = par_mod_qua_stp['parametercache__ident']
            par_name = par_mod_qua_stp['parametercache__name']
            mod = par_mod_qua_stp['modulecache__ident']
            qua = par_mod_qua_stp['qualifiersetcache__ident']
            stp = par_mod_qua_stp['timestepcache__ident']

            instance_slug = '%s_%s_%s_%s_%s' % (slug, par, mod, qua, stp)
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
            if par:
                layer_params.append("par_ident='%s'" % par)
            if mod:
                layer_params.append("mod_ident='%s'" % mod)
            if qua:
                layer_params.append("qua_ident='%s'" % qua)
            if stp:
                layer_params.append("stp_ident='%s'" % stp)
            new_layer.filter = ' and '.join(layer_params)

            # Note that the same name can occur multiple times, but
            # with different mod, qua and/or stp.
            if qua is None:
                new_layer.name = '%s (%s)' % (par_name, stp)
            else:
                new_layer.name = '%s %s (%s)' % (par_name, qua, stp)
            new_layer.name = new_layer.name[:80]
            new_layer.source_ident = source_ident
            new_layer.valid = True
            new_layer.is_local_server = layer.is_local_server
            new_layer.is_clickable = layer.is_local_server
            new_layer.js_popup_class = layer.js_popup_class
            new_layer.save()

            new_layer.tags.add(tag)
            for original_tag in original_tags:
                new_layer.tags.add(original_tag)
            if mod is not None:
                # add tag
                mod_tag, _ = Tag.objects.get_or_create(slug='%s_%s' % (tag, mod))
                new_layer.tags.add(mod_tag)

        logger.info('new %d items' % count_new)
        logger.info('updated %d items' % count_update)
