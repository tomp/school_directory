# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0009_auto_20150902_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='olsclass',
            name='teacher',
            field=models.OneToOneField(related_name='+', null=True, blank=True, to='contacts.Adult'),
        ),
    ]
