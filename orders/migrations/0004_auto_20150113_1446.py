# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20141220_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='type',
            field=models.CharField(verbose_name='Тип заказа', max_length=1, choices=[('0', 'Бронирование столика'), ('1', 'Заказ самовывоза'), ('2', 'Заказ доставки')]),
            preserve_default=True,
        ),
    ]
