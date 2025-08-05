from django.core.management.base import BaseCommand, CommandError
from mockverein.mockdaten import erstelle_mockdaten

class Command(BaseCommand):
    help = "Create mocked user data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        erstelle_mockdaten()
