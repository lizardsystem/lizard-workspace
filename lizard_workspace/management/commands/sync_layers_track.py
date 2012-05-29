from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from lizard_workspace.tasks import sync_layers_track


class Command(BaseCommand):
    help = ("""
create new Layers for trackrecords

Uses a Layer template and some hardcoded criteria

prerequisites
- a Layer as a template

The default is called "vss_track_records", because querying our
/layers/wms (using sync_layers_with_wmsservers) returns a
vss:vss_track_records entry.

Example: bin/django sync_layers_track --slug=<slug of existing Layer>
""")

    option_list = BaseCommand.option_list + (
        make_option('--slug',
                    help='slug of existing Layer',
                    type='str',
                    default='vss_track_records'),)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        slug = options['slug']

        sync_layers_track(slug)
