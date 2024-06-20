# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mitglieder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mitglied',
            name='beitrag_cent',
            field=models.IntegerField(default=1000),
            preserve_default=True,
        ),
    ]
