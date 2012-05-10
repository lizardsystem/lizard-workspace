# Celery tasks
import logging
from celery.task import task
from copy import deepcopy
from django.template.defaultfilters import slugify
from django.utils import simplejson

from lizard_task.handler import get_handler
from lizard_workspace.models import Layer
from lizard_workspace.models import Tag
from lizard_fewsnorm.models import TimeSeriesCache


LOGGER_NAME = 'lizard_workspace_tasks'
logger = logging.getLogger(LOGGER_NAME)


@task
def sync_layers_ekr(slug='vss_area_value', username=None, taskname=None, loglevel=20):
    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
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

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def sync_layers_fewsnorm(
    slug='vss_fews_locations', username=None, taskname=None, loglevel=20):

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
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

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'
