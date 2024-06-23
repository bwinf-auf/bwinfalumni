from django.db import migrations
from datetime import date

def initial_mitgliedsbeitrag(apps, schema_editor):
    # We can't import the Verein model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Verein = apps.get_model("verein", "Verein")

    verein = Verein()
    verein.mitgliedsbeitrag_cent = 1000
    verein.beschlussfassung = date(2000, 10, 27)
    verein.save()

class Migration(migrations.Migration):

    dependencies = [
        ('verein', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_mitgliedsbeitrag),
    ]
