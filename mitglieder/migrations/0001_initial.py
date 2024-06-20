# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('umsaetze', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lastschriftmandat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('kontoinhaber', models.CharField(max_length=250)),
                ('bankname', models.CharField(max_length=250)),
                ('iban', models.CharField(max_length=250)),
                ('bic', models.CharField(max_length=250)),
                ('gueltig_ab', models.DateField(default=datetime.date.today)),
                ('gueltig_bis', models.DateField(default=datetime.date(3000, 1, 1))),
            ],
            options={
                'verbose_name': 'Lastschriftmandat',
                'verbose_name_plural': 'Lastschriftmandate',
                'db_table': 'lastschriftmandat',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mitglied',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('mitgliedsnummer', models.IntegerField(unique=True)),
                ('antragsdatum', models.DateField(default=datetime.date.today)),
                ('beitrittsdatum', models.DateField(default=datetime.date.today, null=True, blank=True)),
                ('austrittsdatum', models.DateField(null=True, blank=True)),
                ('vorname', models.CharField(max_length=250)),
                ('nachname', models.CharField(max_length=250)),
                ('anrede', models.CharField(max_length=250, blank=True)),
                ('geburtsdatum', models.DateField(default=datetime.date(1970, 1, 1))),
                ('strasse', models.CharField(max_length=250)),
                ('adresszusatz', models.CharField(max_length=250, blank=True)),
                ('plz', models.CharField(max_length=10)),
                ('stadt', models.CharField(max_length=250)),
                ('land', models.CharField(max_length=250, default='Deutschland')),
                ('telefon', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=75)),
                ('beruf', models.CharField(max_length=250, blank=True)),
                ('studienort', models.CharField(max_length=250, blank=True)),
                ('studienfach', models.CharField(max_length=250, blank=True)),
                ('kommentar', models.CharField(max_length=2000, blank=True)),
                ('anzahl_mahnungen', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Mitglied',
                'verbose_name_plural': 'Mitglieder',
                'db_table': 'mitglied',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MitgliedskontoBuchung',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cent_wert', models.IntegerField(default=0)),
                ('kommentar', models.CharField(max_length=250, blank=True)),
                ('buchungsdatum', models.DateField(default=datetime.date.today)),
                ('mitglied', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mitglieder.Mitglied')),
            ],
            options={
                'verbose_name': 'Mitgliedskonto-Buchung',
                'verbose_name_plural': 'Mitgliedskonto-Buchungen',
                'db_table': 'mitgliedskonto_buchung',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MitgliedskontoBuchungstyp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('typname', models.CharField(max_length=250)),
            ],
            options={
                'verbose_name': 'Mitgliedskonto-Buchungstyp',
                'verbose_name_plural': 'Mitgliedskonto-Buchungstypen',
                'db_table': 'mitgliedskonto_buchungstyp',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mitgliedskontobuchung',
            name='typ',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mitglieder.MitgliedskontoBuchungstyp'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mitgliedskontobuchung',
            name='umsatz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='umsaetze.Umsatz', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lastschriftmandat',
            name='mitglied',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mitglieder.Mitglied'),
            preserve_default=True,
        ),
    ]
