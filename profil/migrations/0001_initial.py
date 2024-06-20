# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mitglieder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sichtbarkeit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('bereich', models.CharField(max_length=200)),
                ('sache', models.CharField(max_length=200)),
                ('mitglied', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mitglieder.Mitglied')),
            ],
            options={
                'verbose_name': 'Sichtbarkeit',
                'verbose_name_plural': 'Sichtbarkeiten',
                'db_table': 'sichtbarkeit',
            },
            bases=(models.Model,),
        ),
    ]
