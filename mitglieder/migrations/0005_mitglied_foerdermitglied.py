# Generated by Django 4.2.11 on 2024-06-23 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mitglieder', '0004_auto_20210521_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='mitglied',
            name='foerdermitglied',
            field=models.BooleanField(default=False),
        ),
    ]
