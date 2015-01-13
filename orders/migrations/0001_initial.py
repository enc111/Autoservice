# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('autosaloons', '0001_initial'),
        ('employees', '0001_initial'),
        ('cars', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('client_phone', models.CharField(max_length=10, verbose_name='Телефон клиента')),
                ('type', models.CharField(max_length=1, verbose_name='Тип заказа', choices=[('0', 'Боронирование столика'), ('1', 'Заказ самовывоза'), ('2', 'Заказ доставки')])),
                ('state', models.CharField(default='0', max_length=1, verbose_name='Состояние заказа', choices=[('0', 'Не установлен'), ('1', 'На рассмотрении'), ('2', 'Выполняется'), ('3', 'Отменен'), ('4', 'Выполнен')])),
                ('order_date', models.DateField(verbose_name='Дата заказа', auto_now_add=True)),
                ('execute_date', models.DateField(verbose_name='Дата исполнения')),
                ('execute_time', models.TimeField(verbose_name='Время исполнения')),
                ('delivery_address', models.CharField(max_length=50, blank=True, null=True, verbose_name='Адрес доставки')),
                ('contact_account', models.ForeignKey(to='employees.Employee', verbose_name='Контактное лицо организации', related_name='orders')),
                ('dinner_wagon', models.ForeignKey(blank=True, related_name='orders', to='autosaloons.DinnerWagon', null=True, verbose_name='Столик')),
                ('autosaloon_branch', models.ForeignKey(blank=True, related_name='+', to='autosaloons.AutosaloonBranch', null=True, verbose_name='Филиал заведения')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrdersCartRow',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('cares_count', models.IntegerField(default=1, verbose_name='Количество блюд')),
                ('order_date', models.DateField(verbose_name='Дата заказа блюда')),
                ('order_time', models.TimeField(verbose_name='Время заказ блюда')),
                ('autosaloon_car', models.OneToOneField(to='cars.AutosaloonCar', verbose_name='Блюдо заведения')),
                ('order', models.ForeignKey(to='orders.Order', verbose_name='Строка заказа', related_name='rows')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
