from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from lizard_workspace.tasks import sync_layers_fewsnorm as sync_layers_fewsnorm_task


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
        slug = options['slug']
        sync_layers_fewsnorm_task(slug=slug)
