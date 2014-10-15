# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tardy_tracker', '0002_auto_20141014_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='start_time',
            field=models.TimeField(null=True),
        ),
    ]
