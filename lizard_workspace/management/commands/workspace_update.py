# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction

from lizard_workspace.tasks import (
    workspace_update_baselayers,
    workspace_update_watersystem,
    workspace_update_trackrecords,
    workspace_update_minimap,
    workspace_update_thememaps,
    workspace_update_measure,
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
        _option('thememaps', 'Configure thememaps layers'),
        _option('thememapmeasure', 'Configure measure thememaps layers'),
        _option('all', 'All of the above options in one command'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if options.get('baselayers') or options.get('all'):
            workspace_update_baselayers(loglevel=10)
        if options.get('watersystem') or options.get('all'):
            workspace_update_watersystem(loglevel=10)
        if options.get('trackrecords') or options.get('all'):
            workspace_update_trackrecords(loglevel=10)
        if options.get('minimap') or options.get('all'):
            workspace_update_minimap(loglevel=10)
        if options.get('thememaps') or options.get('all'):
            workspace_update_thememaps(loglevel=10)
        if options.get('thememapmeasure') or options.get('all'):
            workspace_update_measure(loglevel=10)
