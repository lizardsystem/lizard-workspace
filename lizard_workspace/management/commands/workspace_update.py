# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_workspace.tasks import (
    workspace_update_baselayers,
    workspace_update_watersystem,
    workspace_update_trackrecords,
    workspace_update_minimap,
)

import optparse


def _option(option, help_text):
    """
    Return an option.
    """
    return optparse.make_option(
        '--' + option,
        action='store_true',
        dest=option,
        default=False,
        help=help_text,
    )


class Command(BaseCommand):
    args = ''
    help = 'Run some updating code based on provided options.'

    option_list = BaseCommand.option_list + (
        _option('baselayers', 'Configure baselayers'),
        _option('watersystem', 'Configure watersystem layers'),
        _option('trackrecords', 'Configure trackrecord layers'),
        _option('minimap', 'Configure minimap layers'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if options.get('baselayers'):
            workspace_update_baselayers(loglevel=10)
        if options.get('watersystem'):
            workspace_update_watersystem(loglevel=10)
        if options.get('trackrecords'):
            workspace_update_trackrecords(loglevel=10)
        if options.get('minimap'):
            workspace_update_minimap(loglevel=10)
