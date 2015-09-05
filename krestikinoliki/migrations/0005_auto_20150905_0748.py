# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('krestikinoliki', '0004_auto_20150904_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='user_message',
            field=models.CharField(default=b'', max_length=48),
        ),
    ]
