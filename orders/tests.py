from django.test import TestCase
from datetime import date, datetime, timedelta

# Create your tests here.

from cars.models import AutosaloonCar
from autosaloons.models import DinnerWagon, BranchHall
from orders.models import Order, OrdersCartRow


class OrderTest(TestCase):
    def test_order_expire_date(self):
        order_test = Order(
            client_phone=8432424,
            type=Order.TYPE_DINNER_WAGON,
            state=Order.STATE_DONE,
            order_date=date(2014, 12, 12),
            execute_date=datetime(2014, 12, 12).date()
        )
        self.assertEqual(
            order_test.expire_date,
            datetime(2015, 1, 11).date(),
            "expire_date is not equal"
        )

    def test_order_make(self):
        order_test = Order(client_phone=8432424,
                           type=Order.TYPE_DINNER_WAGON,
                           state=Order.STATE_DONE,
                           order_date=date(2014, 12, 12),
                           execute_date=datetime(2014, 12, 12).date())
        order_test.make()
        self.assertEqual(order_test.state.__str__(), '4', 'State of order is not equal')
        self.assertEqual(order_test.type, Order.TYPE_DINNER_WAGON)

    def test_order_accept(self):
        order_test = Order(client_phone=8432424,
                           type=Order.TYPE_DINNER_WAGON,
                           state=Order.STATE_DONE,
                           order_date=date(2014, 12, 12),
                           execute_date=datetime(2014, 12, 12).date())
        order_test.accept()
        self.assertEqual(order_test.state, Order.STATE_IN_PROGRESS)

    def test_order_decline(self):
        order_test = Order(
            client_phone=8432424,
            type=Order.TYPE_DINNER_WAGON,
            state=Order.STATE_DONE,
            order_date=date(2014, 12, 12),
            execute_date=datetime(2014, 12, 12).date(),
            dinner_wagon=DinnerWagon(seats=2)
        )
        order_test.decline()
        self.assertEqual(
            order_test.state,
            Order.STATE_CANCELED
        )

    def test_order_perform(self):
        order_test = Order(client_phone=8432424,
                           type=Order.TYPE_DINNER_WAGON,
                           state=Order.STATE_DONE,
                           order_date=date(2014, 12, 12),
                           execute_date=datetime(2014, 12, 12).date(),
                           dinner_wagon=DinnerWagon(seats=2))
        order_test.perform()
        self.assertEqual(order_test.state, Order.STATE_DONE)



