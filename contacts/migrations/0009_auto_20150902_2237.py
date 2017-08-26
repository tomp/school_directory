# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_auto_20150902_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='address',
            field=models.ForeignKey(related_name='+', blank=True, to='contacts.Address', null=True),
        ),
    ]
