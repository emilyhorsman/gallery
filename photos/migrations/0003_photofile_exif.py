# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-10 04:58
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_photofile_is_original'),
    ]

    operations = [
        migrations.AddField(
            model_name='photofile',
            name='exif',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
