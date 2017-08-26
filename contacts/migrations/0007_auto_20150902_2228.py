# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20150902_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adult',
            name='cellphone',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='adult',
            name='email',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='adult',
            name='homephone',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
