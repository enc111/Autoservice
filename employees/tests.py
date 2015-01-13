from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase
# TODO accept_order and decline_order
# Create your tests here.
from employees.models import Employee
from autosaloons.models import Autosaloon
from orders.models import Order
from django.test.client import Client


class EmployeeTest(TestCase):
    def test_employee_str(self):
        est_test = Autosaloon(name="Vaflia project")
        emp_test = Employee(utosaloon=est_test)
        self.assertEqual(emp_test.__str__(), 'Аккаунт Vaflia project')

        # def test_acc_order(self):
        # emp_test=Employee()
        # order_test=Order(state=Order.STATE_UNDER_CONSIDERATION)
        #  emp_test.acc_order(order=order_test)
        # self.assertEqual(order_test.state, Order.STATE_IN_PROGRESS)


class AuthenticateTest(TestCase):
    def test_index(self):
        resp = self.client.get('/employee/accounts/login/')
        self.assertEqual(resp.status_code, 200)

    def test_auth(self):
        self.c = Client()
        self.user = User.objects.create(
            username='testuser',
            password='12345',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.user.set_password('hello')
        self.user.save()
        self.user = auth.authenticate(username='testuser', password='hello')
        login = self.c.login(username='testuser', password='hello')
        self.assertTrue(login)

    def test_auth2(self):
        self.c = Client()
        self.user = auth.authenticate(username='testuser1', password='hello')
        login = self.c.login(username='testuser1', password='hello')
        self.assertFalse(login)
