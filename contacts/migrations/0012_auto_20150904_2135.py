# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0011_auto_20150904_2124'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='olsclass',
            options={'ordering': ('-rank',), 'verbose_name': 'OLS Class', 'verbose_name_plural': 'OLS Classes'},
        ),
        migrations.AlterField(
            model_name='olsclass',
            name='rank',
            field=models.CharField(default=b'', max_length=8),
        ),
    ]
