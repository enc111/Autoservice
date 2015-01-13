# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BranchHall',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('type', models.CharField(max_length=1, verbose_name='Тип зала', choices=[('0', 'Курящий'), ('1', 'Не курящий')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='Название')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DinnerWagon',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('seats', models.IntegerField(default=2, verbose_name='Количество мест')),
                ('hall', models.ForeignKey(blank=True, related_name='dinner_wagons', to='autosaloons.BranchHall', null=True, verbose_name='Зал заведения')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Autosaloon',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('autosaloon_image', models.ImageField(upload_to='autosaloons/', blank=True, null=True, verbose_name='Логотип')),
                ('description', models.CharField(max_length=300, blank=True, null=True, verbose_name='Описание')),
                ('email', models.CharField(max_length=30, unique=True, verbose_name='Электронная почта')),
                ('city', models.ForeignKey(to='autosaloons.City', verbose_name='Город', related_name='autosaloons')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AutosaloonBranch',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('address', models.CharField(max_length=80, verbose_name='Адресс')),
                ('order_phone_number', models.CharField(max_length=10, verbose_name='Телефон заказов')),
                ('help_phone_number', models.CharField(max_length=10, verbose_name='Телефон для справок')),
                ('autosaloon', models.ForeignKey(to='autosaloons.Autosaloon', verbose_name='Заведение', related_name='branches')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='branchhall',
            name='branch',
            field=models.ForeignKey(to='autosaloons.AutosaloonBranch', verbose_name='Филиал заведения', related_name='halls'),
            preserve_default=True,
        ),
    ]
