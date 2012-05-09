# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
import logging
import datetime
from django.db import transaction

from owslib.wms import WebMapService

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from lizard_workspace.models import Tag
from lizard_workspace.models import Layer
from lizard_workspace.models import SyncTask

from lizard_layers.models import ServerMapping

from optparse import make_option

logger = logging.getLogger(__name__)


@transaction.commit_on_success
def perform_sync_task(task):
    logger.info('start with sync of server %s' % task.server.name)

    data_set = task.data_set
    if task.server.is_local_server:
        path_and_parameters = task.server.url.split('?')
        path = path_and_parameters[0]
        regex = r'^' + path + r'/?$'
        external_server = ServerMapping.objects.get(
            relative_path__regex=regex,
        ).external_server
        if len(path_and_parameters) > 1:
            parameters = path_and_parameters[1]
            service_url = external_server + '?' + parameters
        else:
            service_url = external_server
    else:
        service_url = task.server.url
    password = task.server.password
    username = task.server.username

    wms = WebMapService(
        service_url,
        version='1.1.1',
        password=password,
        username=username,
    )

    if task.tag:
        tag, new = task.tag, False
    else:
        tag, new = Tag.objects.get_or_create(
            slug='server_%s' % task.server.name)

    # layers = Layer.objects.filter(server=task.server)
    layers = Layer.objects.filter(source_ident=task.source_ident)

    layer_dict = dict(layers.values_list('layers', 'id'))

    #update server info
    task.server.title = wms.identification.title
    task.server.abstract = wms.identification.abstract
    task.server.save()

    new = 0
    new_names = []
    removed = 0
    removed_names = []
    updated = 0

    for wmslayer in wms.contents:
        if wmslayer in layer_dict:
            layer = layers.get(pk=layer_dict[wmslayer])
            del layer_dict[wmslayer]

            updated += 1
        else:
            layer = Layer()
            layer.server = task.server
            layer.layers = wmslayer
            layer.name = wms[wmslayer].title

            layer.slug = slugify(layer.name)
            layer.save()
            layer.tags.add(tag)

            new += 1
            new_names.append(layer.name)

        layer.data_set = data_set
        layer.is_local_server = task.server.is_local_server
        layer.is_clickable = task.server.is_clickable
        if not layer.js_popup_class and task.server.js_popup_class:
            layer.js_popup_class = task.server.js_popup_class
        layer.valid = True
        if data_set:
            layer.owner_type = Layer.OWNER_TYPE_DATASET
        else:
            layer.owner_type = Layer.OWNER_TYPE_PUBLIC

        layer.source_ident = task.source_ident
        layer.save()

        #nog iets met styles?

    for name, id in layer_dict.items():
        layer = layers.get(pk=id)
        layer.valid = False
        layer.save()

        removed += 1
        removed_names.append(layer.name)

    logger.info('%i new layers: %s.' % (new, str(', '.join(new_names))))
    logger.info('%i updated layers.' % (updated))
    logger.info('%i removed layers: %s.' % (
            removed, str(', '.join(removed_names))))

    task.last_sync = datetime.datetime.now()
    task.last_result = '%i new, %i updated, %i removed' % (
        new, updated, removed)

    task.save()


class Command(BaseCommand):
    help = ("""
Make Layers for all layers found in wmsservers, configured in
SyncTask. Properties can be set in single SyncTasks.

Tags of existing elements will not be deleted. If necessary they will
be extended.

Example: bin/django sync_layers_with_wmsserver --sync_task=<slug of SyncTask> --all=True
""")

    option_list = BaseCommand.option_list + (
        make_option('--sync_task',
                    help='slug of sync_task',
                    type='str',
                    default=None),
        make_option('--all',
                    help='sync all tasks',
                    default=False))

    def handle(self, *args, **options):

        logger.info('start sync')

        if not options['sync_task'] and not options['all']:
            logger.error("Expected --sync_task or --all args. "\
                             "Use -help for example.")
            return

        if options['all']:
            tasks = SyncTask.objects.all()
        else:
            task = SyncTask.objects.get(slug=options['sync_task'])
            tasks = [task]

        for task in tasks:
            try:
                perform_sync_task(task=task)
            except Exception as e:
                logger.error('Something went wrong performing task %s' % task)
                print e
                continue
        return 'Klaar'
