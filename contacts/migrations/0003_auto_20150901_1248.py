# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20150901_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adult',
            name='address',
            field=models.ForeignKey(related_name='+', blank=True, to='contacts.Address', null=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='address',
            field=models.ForeignKey(related_name='+', to='contacts.Address'),
        ),
        migrations.AlterField(
            model_name='olsclass',
            name='aide',
            field=models.ForeignKey(related_name='+', blank=True, to='contacts.Adult', null=True),
        ),
        migrations.AlterField(
            model_name='olsclass',
            name='classmom',
            field=models.ForeignKey(related_name='+', blank=True, to='contacts.Adult', null=True),
        ),
    ]
