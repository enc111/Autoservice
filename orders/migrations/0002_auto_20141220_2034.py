# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderscartrow',
            name='order_date',
            field=models.DateField(verbose_name='На какую дату заказано блюдо'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderscartrow',
            name='order_time',
            field=models.TimeField(verbose_name='На какое время заказано блюдо'),
            preserve_default=True,
        ),
    ]
