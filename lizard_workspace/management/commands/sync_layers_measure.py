from django.db import transaction
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from optparse import make_option

from lizard_workspace.tasks import sync_layers_measure as sync_layers_measure_task


class Command(BaseCommand):
    help = ("""
Use a Layer template and some hardcoded criteria to create new Layers for measures

- a Layer as a template

The default is called "vss_measure", because querying our
/layers/wms (using sync_layers_with_wmsservers) returns a
vss:vss_measure entry.

Example: bin/django sync_layers_measure --slug=<slug of existing Layer>
""")

    option_list = BaseCommand.option_list + (
        make_option('--slug',
                    help='slug of existing Layer',
                    type='str',
                    default='vss_measure'),)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        slug = options['slug']
        sync_layers_measure_task(slug=slug, loglevel=10)
