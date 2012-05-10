# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
from django.db import transaction

from django.core.management.base import BaseCommand

from optparse import make_option

from lizard_workspace.tasks import sync_layers_with_wmsserver as sync_layers_with_wmsserver_task


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

    @transaction.commit_on_success
    def handle(self, *args, **options):

        print 'start sync'

        if not options['sync_task'] and not options['all']:
            print("Expected --sync_task or --all args. "\
                      "Use -help for example.")
            return

        sync_layers_with_wmsserver_task(
            synctask=options['sync_task'],
            all=options['all'],
            loglevel=10)
