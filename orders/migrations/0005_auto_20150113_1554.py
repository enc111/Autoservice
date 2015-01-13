# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20150113_1446'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderscartrow',
            old_name='cares_count',
            new_name='cars_count',
        ),
    ]
