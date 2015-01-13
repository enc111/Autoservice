from datetime import timedelta
from django.db import models
from cars.models import AutosaloonCar
from employees.models import Employee
from autosaloons.models import AutosaloonBranch, DinnerWagon


class Order(models.Model):
    STATE_NONE = '0'
    STATE_UNDER_CONSIDERATION = '1'
    STATE_IN_PROGRESS = '2'
    STATE_CANCELED = '3'
    STATE_DONE = '4'

    ORDER_STATE = (
        (STATE_NONE, 'Не установлен'),
        (STATE_UNDER_CONSIDERATION, 'На рассмотрении'),
        (STATE_IN_PROGRESS, 'Выполняется'),
        (STATE_CANCELED, 'Отменен'),
        (STATE_DONE, 'Выполнен'),
    )

    TYPE_DINNER_WAGON = '0'
    TYPE_PICKUP = '1'
    TYPE_DELIVERY = '2'

    ORDER_TYPE = (
        (TYPE_DINNER_WAGON, 'Бронирование столика'),
        (TYPE_PICKUP, 'Заказ самовывоза'),
        (TYPE_DELIVERY, 'Заказ доставки'),
    )

    client_phone = models.CharField(
        max_length=10,
        verbose_name='Телефон клиента'
    )
    type = models.CharField(
        max_length=1,
        choices=ORDER_TYPE,
        verbose_name='Тип заказа'
    )

    state = models.CharField(
        max_length=1,
        choices=ORDER_STATE,
        default=STATE_NONE,
        verbose_name='Состояние заказа'
    )
    order_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата заказа'
    )

    execute_date = models.DateField(verbose_name='Дата исполнения')

    execute_time = models.TimeField(verbose_name='Время исполнения')

    @property
    def expire_date(self):
        if self.state == self.STATE_DONE:
            return self.execute_date + timedelta(days=30)

    contact_account = models.ForeignKey(
        Employee,
        related_name='orders',
        verbose_name='Контактное лицо организации'
    )
    # особенные поля, необходимые для определенных видов заказов

    # для заказа самовывоза и бронирования столика
    autosaloon_branch = models.ForeignKey(
        AutosaloonBranch,
        blank=True,
        null=True,
        related_name='+',
        verbose_name='Филиал заведения'
    )
    # для заказа столика
    dinner_wagon = models.ForeignKey(
        DinnerWagon,
        blank=True,
        null=True,
        related_name='orders',
        verbose_name='Столик'
    )
    # для доставки
    delivery_address = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Адрес доставки'
    )

    # arguments: type='table' or type='pickup 'or type='delivery'
    def make(self, **kwargs):
        if kwargs.get('type') is not None:
            if kwargs.get('type') == 'table':
                self.type = self.TYPE_DINNER_WAGON
                self.state = self.STATE_UNDER_CONSIDERATION
            elif kwargs.get('type') == 'pickup':
                self.type = self.TYPE_PICKUP
                self.state = self.STATE_UNDER_CONSIDERATION
            elif kwargs.get('type') == 'delivery':
                self.type = self.TYPE_DELIVERY
                self.state = self.STATE_UNDER_CONSIDERATION

    def accept(self):
        self.state = self.STATE_IN_PROGRESS

    def decline(self):
        self.state = self.STATE_CANCELED

    def perform(self):
        self.state = self.STATE_DONE

    def __str__(self):
        return \
            self.client_phone.__str__() + \
            " " + self.execute_date.__str__() + \
            " " + self.execute_time.__str__() + \
            " " + self.get_type_display() + \
            " " + self.contact_account.__str__()

    def delete(self, using=None):
        super().delete(using)
        OrdersCartRow.objects.filter(order=self).delete()


class OrdersCartRow(models.Model):
    autosaloon_car = models.ForeignKey(
        AutosaloonCar,
        verbose_name='Блюдо заведения'
    )
    cars_count = models.IntegerField(
        default=1,
        verbose_name='Количество блюд'
    )
    order = models.ForeignKey(
        Order,
        related_name='rows',
        verbose_name='Строка заказа'
    )
