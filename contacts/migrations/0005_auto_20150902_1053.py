# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_family_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'verbose_name_plural': 'Families'},
        ),
        migrations.AlterModelOptions(
            name='olsclass',
            options={'verbose_name': 'OLS Class', 'verbose_name_plural': 'OLS Classes'},
        ),
        migrations.AlterField(
            model_name='family',
            name='address',
            field=models.OneToOneField(related_name='+', to='contacts.Address'),
        ),
        migrations.AlterField(
            model_name='guardian',
            name='person',
            field=models.OneToOneField(to='contacts.Adult'),
        ),
        migrations.AlterField(
            model_name='olsclass',
            name='teacher',
            field=models.OneToOneField(related_name='+', to='contacts.Adult'),
        ),
    ]
