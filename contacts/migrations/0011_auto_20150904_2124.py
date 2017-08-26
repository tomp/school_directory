# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0010_auto_20150902_2319'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ('-city', 'street')},
        ),
        migrations.AlterModelOptions(
            name='adult',
            options={'ordering': ('lastname', 'firstname')},
        ),
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ('name',), 'verbose_name_plural': 'Families'},
        ),
        migrations.AlterModelOptions(
            name='guardian',
            options={'ordering': ('person',)},
        ),
        migrations.AlterModelOptions(
            name='olsclass',
            options={'ordering': ('gradelevel',), 'verbose_name': 'OLS Class', 'verbose_name_plural': 'OLS Classes'},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ('lastname', 'firstname')},
        ),
        migrations.AddField(
            model_name='olsclass',
            name='rank',
            field=models.IntegerField(default=-1),
        ),
    ]
