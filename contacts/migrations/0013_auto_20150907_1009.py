# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0012_auto_20150904_2135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adult',
            name='address',
        ),
        migrations.AlterField(
            model_name='guardian',
            name='relation',
            field=models.CharField(max_length=32, choices=[(b'Mother', b'Mother'), (b'Father', b'Father'), (b'Aunt', b'Aunt'), (b'Uncle', b'Uncle'), (b'Grandmother', b'Grandmother'), (b'Grandfather', b'Grandfather'), (b'Guardian', b'Guardian')]),
        ),
    ]
