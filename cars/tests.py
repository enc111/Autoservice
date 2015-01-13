from django.test import TestCase
from cars.models import Car, AutosaloonCar
from autosaloons.models import Autosaloon, City


class CarTest(TestCase):
    def test_car_class_name(self):
        car = Car(
            name='Гречка',
            price=70.50,
            category=Car.CAR_TYPE_GARNISH,
        )
        self.assertEqual(
            car.__str__(),
            'Гречка', "Имя класса неверно"
        )


class AutosaloonCarTest(TestCase):
    def test_autosaloon_car_class_name(self):
        car = Car(
            name='Паста с курицей',
            price=170.34,
            category=Car.CAR_TYPE_HOT_CAR,
        )
        city = City(
            name='Tomsk',
        )
        autosaloon = Autosaloon(
            name='Пельмени Project',
            city=city,
            email='pelproj@tomsk.ru',
        )

        autosaloon_car = AutosaloonCar(
            car=car,
            autosaloon=autosaloon,
        )
        self.assertEqual(autosaloon_car.__str__(), 'Пельмени Project: Паста с курицей',
                         "Имя класса неверно")
