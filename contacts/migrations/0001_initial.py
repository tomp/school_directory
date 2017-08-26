# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=64)),
                ('city', models.CharField(max_length=64)),
                ('state', models.CharField(max_length=16)),
                ('zipcode', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Adult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=64)),
                ('lastname', models.CharField(max_length=64)),
                ('email', models.CharField(max_length=64)),
                ('homephone', models.CharField(max_length=32)),
                ('cellphone', models.CharField(max_length=32)),
                ('address', models.ForeignKey(to='contacts.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=64)),
                ('private', models.BooleanField()),
                ('address', models.ForeignKey(to='contacts.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Guardian',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation', models.CharField(max_length=32)),
                ('family', models.ForeignKey(to='contacts.Family')),
                ('person', models.ForeignKey(to='contacts.Adult')),
            ],
        ),
        migrations.CreateModel(
            name='OLSClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('grade', models.CharField(max_length=16)),
                ('gradelevel', models.CharField(max_length=16)),
                ('aide', models.ForeignKey(related_name='+', to='contacts.Adult')),
                ('classmom', models.ForeignKey(related_name='+', to='contacts.Adult')),
                ('teacher', models.ForeignKey(related_name='+', to='contacts.Adult')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=64)),
                ('lastname', models.CharField(max_length=64)),
                ('family', models.ForeignKey(to='contacts.Family')),
                ('olsclass', models.ForeignKey(to='contacts.OLSClass')),
            ],
        ),
    ]
