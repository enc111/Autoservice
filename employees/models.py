from django.contrib.auth.models import User
from django.db import models
from autosaloons.models import Autosaloon


class Employee(models.Model):
    user = models.ForeignKey(
        User,
        related_name='autosaloons_accounts',
        verbose_name='Пользователь'
    )
    autosaloon = models.OneToOneField(
        Autosaloon,
        related_name='account',
        verbose_name='Заведение'
    )

    def __str__(self):
        return 'Аккаунт {0}'.format(
            self.autosaloon
        )

    # arguments: order_id = order_id
    # @staticmethod
    # def acc_order(**kwargs):
    #     order_id = kwargs.get('order_id')
    #     if order_id is not None:
    #         necessary_order = Order.objects.filter(id=order_id)
    #         necessary_order.accept()
    #         necessary_order.save(update_fields=['state'])
    #
    # # arguments: order_id = order_id
    # @staticmethod
    # def dec_order(**kwargs):
    #     order_id = kwargs.get('order_id')
    #     if order_id is not None:
    #         necessary_order = Order.objects.filter(id=order_id)
    #         necessary_order.decline()
    #         necessary_order.save(update_fields=['state'])
