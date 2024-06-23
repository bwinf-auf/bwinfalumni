from django.apps import apps
from django.test import TransactionTestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

## This is only a test for a single migration that's supposed to be run only once.
## Delete immediately if it breaks after adding additional migrations.

# From https://stackoverflow.com/a/56212859/20133080
class TestMigrations(TransactionTestCase):
    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to     properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]

        with connection.cursor() as c:
            c.execute("DELETE FROM django_migrations WHERE app='mitglieder' AND name='0006_auto_20240624_0029'")

        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        executor.loader.build_graph()  # reload.
        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass

class FoerdermitgliedMigrationTests(TestMigrations):

    migrate_from = '0005_mitglied_foerdermitglied'
    migrate_to = '0006_auto_20240624_0029'

    def setUpBeforeMigration(self, apps):
        Mitglied = apps.get_model('mitglieder', 'Mitglied')

        Mitglied.objects.create(mitgliedsnummer=1, beitrag_cent=1000)
        Mitglied.objects.create(mitgliedsnummer=2, beitrag_cent=5000)
        Mitglied.objects.create(mitgliedsnummer=3, beitrag_cent=1000)
        Mitglied.objects.create(mitgliedsnummer=4, beitrag_cent=20000)


    def test_tags_migrated(self):
        Mitglied = apps.get_model('mitglieder', 'Mitglied')

        self.assertEqual(1000, Mitglied.objects.get(mitgliedsnummer=1).beitrag_cent)
        self.assertEqual(False, Mitglied.objects.get(mitgliedsnummer=1).foerdermitglied)

        self.assertEqual(5000, Mitglied.objects.get(mitgliedsnummer=2).beitrag_cent)
        self.assertEqual(True, Mitglied.objects.get(mitgliedsnummer=2).foerdermitglied)

        self.assertEqual(1000, Mitglied.objects.get(mitgliedsnummer=3).beitrag_cent)
        self.assertEqual(False, Mitglied.objects.get(mitgliedsnummer=3).foerdermitglied)

        self.assertEqual(20000, Mitglied.objects.get(mitgliedsnummer=4).beitrag_cent)
        self.assertEqual(True, Mitglied.objects.get(mitgliedsnummer=4).foerdermitglied)
