# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Konto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('kontoname', models.CharField(max_length=250)),
                ('beschreibung', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name': 'Konto',
                'verbose_name_plural': 'Konten',
                'db_table': 'konto',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Umsatz',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('text', models.CharField(max_length=250)),
                ('cent_wert', models.IntegerField(default=0)),
                ('beleg', models.CharField(max_length=250)),
                ('author', models.CharField(max_length=250)),
                ('geschaeftspartner', models.CharField(max_length=250)),
                ('wertstellungsdatum', models.DateField(default=datetime.date.today)),
                ('kommentar', models.CharField(max_length=250, blank=True)),
                ('konto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='umsaetze.Konto')),
            ],
            options={
                'verbose_name': 'Umsatz',
                'verbose_name_plural': 'Umsätze',
                'db_table': 'umsatz',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UmsatzTyp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('typname', models.CharField(max_length=250)),
                ('beschreibung', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name': 'Umsatztyp',
                'verbose_name_plural': 'Umsatztypen',
                'db_table': 'umsatztyp',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='umsatz',
            name='typ',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='umsaetze.UmsatzTyp'),
            preserve_default=True,
        ),
    ]
