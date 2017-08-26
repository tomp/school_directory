# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_auto_20150901_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='name',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
