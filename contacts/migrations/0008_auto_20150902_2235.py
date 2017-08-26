# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_auto_20150902_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='address',
            field=models.OneToOneField(related_name='+', null=True, blank=True, to='contacts.Address'),
        ),
    ]
