# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player_first', models.IntegerField()),
                ('player_second', models.IntegerField()),
                ('is_started', models.BooleanField(default=False)),
                ('user_message_code', models.IntegerField(default=0, choices=[(0, b'None'), (1, b'Accept'), (2, b'Reject')])),
            ],
        ),
    ]
