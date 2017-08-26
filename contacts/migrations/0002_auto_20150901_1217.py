# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adult',
            name='address',
            field=models.ForeignKey(to='contacts.Address', blank=True),
        ),
        migrations.AlterField(
            model_name='adult',
            name='cellphone',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AlterField(
            model_name='adult',
            name='email',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='adult',
            name='homephone',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AlterField(
            model_name='olsclass',
            name='aide',
            field=models.ForeignKey(related_name='+', blank=True, to='contacts.Adult'),
        ),
        migrations.AlterField(
            model_name='olsclass',
            name='classmom',
            field=models.ForeignKey(related_name='+', blank=True, to='contacts.Adult'),
        ),
    ]
