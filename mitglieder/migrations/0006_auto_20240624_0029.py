# Generated by Django 4.2.11 on 2024-06-23 22:29

from django.db import migrations


def set_foerdermitglied(apps, schema_editor):
    # We can't import the Mitglied model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Mitglied = apps.get_model("mitglieder", "Mitglied")
    for mitglied in Mitglied.objects.all():

        mitglied.foerdermitglied = mitglied.beitrag_cent != 1000
        mitglied.save()

class Migration(migrations.Migration):

    dependencies = [
        ('mitglieder', '0005_mitglied_foerdermitglied'),
    ]

    operations = [
        migrations.RunPython(set_foerdermitglied),
    ]
