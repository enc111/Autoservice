# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='autosaloon',
            field=models.OneToOneField(to='autosaloons.Autosaloon', related_name='account', verbose_name='Заведение'),
            preserve_default=True,
        ),
    ]
