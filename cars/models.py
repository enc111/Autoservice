from django.db import models
from autosaloons.models import Autosaloon


class Car(models.Model):
    CAR_TYPE_ALCOHOL = '0'
    CAR_TYPE_SOFT_DRINK = '1'
    CAR_TYPE_GARNISH = '2'
    CAR_TYPE_HOT_DISH = '3'
    CAR_TYPE_DESSERT = '4'
    CAR_TYPE_SNAKE = '5'
    CAR_TYPE_SALAD = '6'
    CAR_TYPE_PIZZA = '7'
    CAR_TYPE_ROLL = '8'
    CAR_TYPE_SOUP = '9'

    CAR_TYPE = (
        (CAR_TYPE_ALCOHOL, 'Алкогольные напитки'),
        (CAR_TYPE_SOFT_DRINK, 'Безалкогольные напитки'),
        (CAR_TYPE_GARNISH, 'Гарниры'),
        (CAR_TYPE_HOT_DISH, 'Горячие блюда'),
        (CAR_TYPE_DESSERT, 'Дессерты'),
        (CAR_TYPE_SNAKE, 'Закуски'),
        (CAR_TYPE_SALAD, 'Салаты'),
        (CAR_TYPE_PIZZA, 'Пиццы'),
        (CAR_TYPE_ROLL, 'Роллы'),
        (CAR_TYPE_SOUP, 'Супы'),
    )

    name = models.CharField(
        max_length=30,
        verbose_name='Название'
    )
    description = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    composition = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name='Состав'
    )
    car_image = models.ImageField(
        upload_to='cars/',
        blank=True,
        null=True,
        verbose_name='Картинка блюда',
    )
    weight = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Вес'
    )
    price = models.FloatField(
        default=100.0,
        verbose_name='Цена'
    )
    category = models.CharField(
        max_length=1,
        choices=CAR_TYPE,
        verbose_name='Категория блюда'
    )

    def __str__(self):
        return self.name


class AutosaloonCar(models.Model):
    car = models.OneToOneField(
        Car,
        verbose_name='Блюдо'
    )
    autosaloon = models.ForeignKey(
        Autosaloon,
        related_name='cars',
        verbose_name='Заведение'
    )

    def __str__(self):
        return '{0}: {1}'.format(
            self.autosaloon,
            self.car,
        )
