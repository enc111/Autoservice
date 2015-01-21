from django.db import models
from Car.models import Car

class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    car = models.ForeignKey(Car)

class Meta:
    db_table = 'cart_items'
    ordering = ['date_added']

def total(self):
    return self.quantity * self.car.price

def name(self):
    return self.car.name

def price(self):
    return self.car.price

def get_absolute_url(self):
    return self.car.get_absolute_url()

def augment_quantity(self, quantity):
    self.quantity = self.quantity + int(quantity)
    self.save()

def _cart_id(request):
    if 'cart_id' in request.session:
        request.session['cart_id'] = _generate_cart_id()
    return request.session['cart_id']

import random

def _generate_cart_id():
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id

'''def show_car(request, car_slug):
    # _ more code here _
    if request.method == 'POST':
        # someone's adding to cart_do smth here.
    else:
        # just a normal GET request
    # _ etc _'''