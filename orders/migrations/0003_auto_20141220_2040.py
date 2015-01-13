# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20141220_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderscartrow',
            name='order_date',
        ),
        migrations.RemoveField(
            model_name='orderscartrow',
            name='order_time',
        ),
        migrations.AlterField(
            model_name='orderscartrow',
            name='autosaloon_car',
            field=models.ForeignKey(to='cars.AutosaloonCar', verbose_name='Блюдо заведения'),
            preserve_default=True,
        ),
    ]
