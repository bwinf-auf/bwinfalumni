# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('mitglieder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenutzerMitglied',
            fields=[
                ('benutzer', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, serialize=False, primary_key=True)),
                ('mitglied', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mitglieder.Mitglied')),
            ],
            options={
                'verbose_name': 'Benutzer-Mitglied-Relation',
                'verbose_name_plural': 'Benutzer-Mitglied-Relationen',
                'db_table': 'benutzer_mitglied_relation',
            },
            bases=(models.Model,),
        ),
    ]
