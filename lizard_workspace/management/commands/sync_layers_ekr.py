from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from lizard_workspace.tasks import sync_layers_ekr as sync_layers_ekr_task


class Command(BaseCommand):
    help = ("""
create new Layers for ekr scores

Uses a Layer template and some hardcoded criteria

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
        slug = options['slug']

        sync_layers_ekr_task(slug)
