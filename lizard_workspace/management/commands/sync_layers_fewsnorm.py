import logging

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
(params, qualifiersets).

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
                    default='fews_locations'),)

    def handle(self, *args, **options):
        logger.info('start sync')
        slug = options['slug']
        layer = Layer.objects.get(slug=slug)
        logger.info('template: %s' % layer)

        tag, _ = Tag.objects.get_or_create(slug='fewsnorm_%s' % slug)
        logger.info('tag: %s' % tag)

        logger.debug('Invalidating existing layers...')
        existing_layers = dict(
            (l.slug, l) for l in
            Layer.objects.filter(slug__startswith=slug))
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

            instance_slug = '%s_%s_%s_%s' % (slug, par, qua, stp)
            # Layers can be processed multiple times when multiple
            # modules exist. It doesn't harm.
            if instance_slug in existing_layers:
                # Update existing, the old existing tags have been
                # removed already.
                new_layer = existing_layers[instance_slug]
                logger.debug('Update: %s' % instance_slug)
                count_update += 1
            else:
                # New
                logger.debug('New: %s' % instance_slug)
                new_layer = deepcopy(layer)
                new_layer.slug = instance_slug
                new_layer.id = None
                count_new += 1

            if qua is None:
                new_layer.name = '%s (%s)' % (par, stp)
            else:
                new_layer.name = '%s %s (%s)' % (par, qua, stp)
            new_layer.source_ident = 'fewsnorm::%s' % slug
            new_layer.valid = True
            new_layer.save()

            new_layer.tags.add(tag)
            if mod is not None:
                # add tag
                mod_tag, _ = Tag.objects.get_or_create(slug='%s_%s' % (tag, mod))
                new_layer.tags.add(mod_tag)

        logger.info('new %d items' % count_new)
        logger.info('updated %d items' % count_update)
