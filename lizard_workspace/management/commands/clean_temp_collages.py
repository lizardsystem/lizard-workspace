from django.db import transaction
from django.core.management.base import BaseCommand
from optparse import make_option

from lizard_workspace.tasks import cleanup_temp_collages


class Command(BaseCommand):
    help = ("""
Example: bin/django clean_temp_collages
""")


    @transaction.commit_on_success
    def handle(self, *args, **options):

        cleanup_temp_collages()
