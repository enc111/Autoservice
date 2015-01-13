from django.http import HttpResponse
from django.views.generic import ListView
from cars.models import AutosaloonCar, Car


class CarsList(ListView):
    model = AutosaloonCar
    template_name = 'cars/cars.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        autosaloon_id = self.kwargs.get('autosaloon_id')
        if autosaloon_id is not None:
            if AutosaloonCar.objects.filter(autosaloon__id=autosaloon_id).exists():
                current_autosaloon = AutosaloonCar.objects.filter(autosaloon__id=autosaloon_id)[0]
            else:
                current_autosaloon = AutosaloonCar.objects.first()
        else:
            current_autosaloon = AutosaloonCar.objects.first()

        car_category = self.kwargs.get('car_category')
        default_car_category = car_category or '100'
        context['current_autosaloon'] = current_autosaloon.autosaloon
        context['car_categories_list'] = Car.CAR_TYPE
        context['default_car_category'] = default_car_category
        if default_car_category != '100':
            context['cares_list'] = Car.objects.filter(
                autosalooncar__autosaloon=autosaloon_id,
                category=default_car_category,
            )
        else:
            context['cares_list'] = Car.objects.filter(
                autosalooncar__autosaloon=autosaloon_id
            )
        return context


class CarAbout(ListView):
    model = AutosaloonCar
    template_name = 'cars/car_about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car_id = self.kwargs.get('car_id')
        context['car'] = Car.objects.get(id=car_id)
        return context


def load_cart(request):
    """Загружает сохраненное состояние корзины"""
    if request.is_ajax():
        if request.session.get('cart_price') is not None:
            cart_price = request.session.get('cart_price')
        else:
            cart_price = 0
        message = cart_price
    else:
        message = 'error'
    return HttpResponse(message)


def add_car(request):
    """Добавляет в сессию блюдо, обновляет значение корзины в сессии"""
    if request.is_ajax():
        car_id = request.GET.get('id')
        if request.session.get(car_id) is not None:
            request.session[car_id] += 1
        else:
            request.session[car_id] = 1

        car = Car.objects.get(id=car_id)
        if request.session.get('cart_price') is not None:
            request.session['cart_price'] += car.price
        else:
            request.session['cart_price'] = car.price

        message = 'ok'
    else:
        message = 'error'
    return HttpResponse(message)
