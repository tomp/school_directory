# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20150902_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
