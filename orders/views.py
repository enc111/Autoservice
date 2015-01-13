from datetime import datetime
import time
import json
from django.http import HttpResponse
from django.shortcuts import render
from cars.models import AutosaloonCar, Car
from employees.models import Employee
from autosaloons.models import AutosaloonBranch, DinnerWagon, Autosaloon
from orders.models import Order, OrdersCartRow
from orders.forms import TableForm, UserOrdersForm
from orders.forms import DeliveryForm
from orders.forms import PickUpForm


def view_cart(request, cart_state):
    """Отображает страницу корзины заказа"""
    """cart_state == '1' - загружаем из сессии параметры корзины"""
    """cart_state == '0' - очищаем ключи сессии, загружаем пустую корзину"""
    if cart_state == '0':
        request.session.flush()
        cart_price = 0
        return render(
            request,
            'orders/cart.html',
            {
                'cart_price': cart_price
            }
        )
    else:
        if request.session.get('cart_price') is not None:
            cart_price = request.session.get('cart_price')
        else:
            cart_price = 0

        if cart_price == 0:
            return render(
                request,
                'orders/cart.html',
                {
                    'cart_price': cart_price
                }
            )
        else:
            cares = {}
            for key in request.session.keys():
                if key != 'cart_price':
                    cares[AutosaloonCar.objects.get(car__id=key)] = request.session.get(key)
            cart_cares = cares.items()
            return render(
                request,
                'orders/cart.html',
                {
                    'cart_price': cart_price,
                    'cart_cares': cart_cares,
                }
            )


def view_orders(request):
    """Отображает страницу подготовленных заказов"""
    order_autosaloons = []
    for key in request.session.keys():
        if key != 'cart_price':
            first_autosaloon_for_key = AutosaloonCar.objects.filter(car__id=int(key))[0].autosaloon
            if order_autosaloons.count(first_autosaloon_for_key) == 0:
                order_autosaloons.append(first_autosaloon_for_key)

    orders_in_cart = {}
    for autosaloon in order_autosaloons:
        autosaloon_order_price = 0
        for key in request.session.keys():
            if key != 'cart_price':
                if AutosaloonCar.objects.filter(car__id=int(key))[0].autosaloon.name == autosaloon.name:
                    autosaloon_order_price += \
                        request.session[key] *\
                        AutosaloonCar.objects.get(car__id=int(key)).car.price
        orders_in_cart[autosaloon] = autosaloon_order_price

    orders = orders_in_cart.items()

    return render(
        request,
        'orders/cart_orders.html',
        {
            'orders': orders
        }
    )


def view_autosaloon_car_list(request):
    """Возвращает список блюд в заказе, относящиеся к определенному заведению"""
    if request.is_ajax():
        autosaloon_id = request.GET.get('id')
        autosaloon = AutosaloonCar.objects.filter(autosaloon__id=int(autosaloon_id))[0].autosaloon
        autosaloon_cares_in_order = {}
        for key in request.session.keys():
            if key != 'cart_price':
                if AutosaloonCar.objects.filter(car__id=int(key))[0].autosaloon.name == autosaloon.name:
                    autosaloon_cares_in_order[Car.objects.get(id=int(key))] = request.session[key]

        car_list = []
        for key, val in autosaloon_cares_in_order.items():
            car_specification = {'car_name': key.name, 'car_price': key.price, 'car_count': val}
            car_list.append(car_specification)

        json_string = json.dumps(car_list, ensure_ascii=False).encode('utf8')
        return HttpResponse(json_string)
    else:
        return HttpResponse('error')


def increment_car(request):
    """Увеличивает количество единиц заданного блюда на 1"""
    if request.is_ajax():
        car_id = request.GET.get('id')
        car_price = request.GET.get('price')
        request.session[car_id] += 1
        request.session['cart_price'] += float(car_price)
        return HttpResponse(request.session[car_id])
    else:
        return HttpResponse('error')


def decrement_car(request):
    """Уменьшает количество единиц заданного блюда на 1"""
    if request.is_ajax():
        car_id = request.GET.get('id')
        car_count = request.GET.get('count')
        old_count = request.session.get(car_id)
        dec_price = Car.objects.get(id=car_id).price * int(car_count)
        if old_count - int(car_count) <= 0:
            del request.session[car_id]
            old_cart_price = request.session.get('cart_price')
            if old_cart_price - dec_price <= 0:
                del request.session['cart_price']
            else:
                request.session['cart_price'] -= dec_price
        else:
            request.session[car_id] -= int(car_count)
            request.session['cart_price'] -= dec_price
        if request.session.get(car_id) is not None:
            return HttpResponse(request.session[car_id])
        else:
            return HttpResponse(0)
    else:
        return HttpResponse('error')


def get_order_form(request, autosaloon_id, order_type):
    """Возвращает на страницу соответствующую форму, тип зависит от order_type:
    0 - заказ столика
    1 - заказ самовывоза
    2 - заказ доставки"""
    # проверям, нужно ли вообще пользователю показывать форму (вдруг он ничего не заказал?)
    # проверяем, есть ли в сессии ключи, соответствующие блюдам выбранного заведения
    autosaloon_cares = Car.objects.filter(autosalooncar__autosaloon__id=autosaloon_id)
    is_valid_request = False
    for key in request.session.keys():
        if key != 'cart_price':
            if autosaloon_cares.filter(id=key).first() is not None:
                is_valid_request = True
                break

    if is_valid_request:
        order_types = Order.ORDER_TYPE
        if order_type == '1':
            if request.method == 'POST':
                form = PickUpForm(autosaloon_id, request.POST)
                if form.is_valid():
                    order_client_phone = form.cleaned_data['phone']
                    order_order_type = order_type
                    order_execute_date = form.cleaned_data['date']
                    order_execute_time = form.cleaned_data['time']
                    order_contact_account = Employee.objects.filter(
                        autosaloon__id=autosaloon_id
                    ).first()
                    order_branch_id = int(request.POST.get('address'))
                    order_autosaloon_branch = AutosaloonBranch.objects.filter(
                        id=order_branch_id
                    ).first()
                    new_order = Order(
                        client_phone=order_client_phone,
                        type=order_order_type,
                        execute_date=order_execute_date,
                        execute_time=order_execute_time,
                        contact_account=order_contact_account,
                        autosaloon_branch=order_autosaloon_branch
                    )
                    new_order.save()
                    for key in request.session.keys():
                        if key != 'cart_price':
                            row = OrdersCartRow(
                                autosaloon_car=AutosaloonCar.objects.get(car__id=key),
                                cares_count=request.session[key],
                                order=new_order,
                            )
                            row.save()
                    new_order.make(type='pickup')
                    new_order.save(update_fields=['type', 'state'])

                    # удаление из сессии оформленных в заказе блюд и корзины, при необходимости
                    keys_for_delete = []
                    for key in request.session.keys():
                        if key != 'cart_price':
                            if autosaloon_cares.get(id=key) is not None:
                                keys_for_delete.append(key)
                    for key in keys_for_delete:
                        del request.session[key]
                    is_cart_empty = True
                    for key in request.session.keys():
                        if key != 'cart_price':
                            is_cart_empty = False
                    if is_cart_empty:
                        del request.session['cart_price']

                    autosaloon = Autosaloon.objects.get(id=autosaloon_id)
                    return render(
                        request,
                        'orders/order_created.html',
                        {
                            'order_type': order_type,
                            'autosaloon_id': autosaloon_id,
                            'autosaloon_name': autosaloon.name,
                            'autosaloon_email': autosaloon.email,
                            'autosaloon_branch_order_phone': order_autosaloon_branch.order_phone_number,
                            'autosaloon_branch_help_phone': order_autosaloon_branch.help_phone_number
                        }
                    )
                else:
                    if request.POST.get('address_changed') == '1':
                        show_errors = 0
                    else:
                        show_errors = 1
            else:
                form = PickUpForm(autosaloon_id)
                show_errors = 0
            return render(
                request,
                'orders/make_order_form.html',
                {
                    # show_form определяет, нужно ли показывать форму пользователю
                    'show_form': 1,
                    'show_errors': show_errors,
                    'autosaloon_id': autosaloon_id,
                    'form': form,
                    'order_types_list': order_types,
                    'current_order_type': order_type
                }
            )
        elif order_type == '2':
            if request.method == 'POST':
                form = DeliveryForm(request.POST)
                if form.is_valid():
                    order_client_phone = form.cleaned_data['phone']
                    order_order_type = order_type
                    order_execute_date = form.cleaned_data['date']
                    order_execute_time = form.cleaned_data['time']
                    order_contact_account = Employee.objects.filter(
                        autosaloon__id=autosaloon_id
                    ).first()
                    order_delivery_address = request.POST.get('address')
                    new_order = Order(
                        client_phone=order_client_phone,
                        type=order_order_type,
                        execute_date=order_execute_date,
                        execute_time=order_execute_time,
                        contact_account=order_contact_account,
                        delivery_address=order_delivery_address
                    )
                    new_order.save()
                    for key in request.session.keys():
                        if key != 'cart_price':
                            row = OrdersCartRow(
                                autosaloon_car=AutosaloonCar.objects.get(car__id=key),
                                cares_count=request.session[key],
                                order=new_order,
                            )
                            row.save()
                    new_order.make(type='delivery')
                    new_order.save(update_fields=['type', 'state'])

                    # удаление из сессии оформленных в заказе блюд и корзины, при необходимости
                    keys_for_delete = []
                    for key in request.session.keys():
                        if key != 'cart_price':
                            if autosaloon_cares.get(id=key) is not None:
                                keys_for_delete.append(key)
                    for key in keys_for_delete:
                        del request.session[key]
                    is_cart_empty = True
                    for key in request.session.keys():
                        if key != 'cart_price':
                            is_cart_empty = False
                    if is_cart_empty:
                        del request.session['cart_price']

                    autosaloon = Autosaloon.objects.get(id=autosaloon_id)
                    return render(
                        request,
                        'orders/order_created.html',
                        {
                            'order_type': order_type,
                            'autosaloon_id': autosaloon_id,
                            'autosaloon_name': autosaloon.name,
                            'autosaloon_email': autosaloon.email,
                            'autosaloon_branch_order_phone': '',
                            'autosaloon_branch_help_phone': ''
                        }
                    )
            else:
                form = DeliveryForm()
            show_errors = 1
            return render(
                request,
                'orders/make_order_form.html',
                {
                    # show_form определяет, нужно ли показывать форму пользователю
                    'show_form': 1,
                    'show_errors': show_errors,
                    'autosaloon_id': autosaloon_id,
                    'form': form,
                    'order_types_list': order_types,
                    'current_order_type': order_type
                }
            )
        else:
            if request.method == 'POST':
                if request.POST.get('address_changed') == '1':
                    # выб выбран другой филиал заведения
                    branch_id = request.POST.get('address')
                    form = TableForm(autosaloon_id, branch_id, -1, -1, request.POST)
                    show_errors = 0
                    show_custom_date_error = 0
                elif request.POST.get('show_tables') == '1':
                    # была нажата кнопка показа столиков
                    branch_id = request.POST.get('address')
                    hall_type = request.POST.get('hall')
                    order_date_str = request.POST.get('date')
                    try:
                        time_structure = time.strptime(order_date_str, '%Y-%m-%d')
                        order_date = datetime(time_structure.tm_year, time_structure.tm_mon, time_structure.tm_mday)
                        border_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
                        if order_date < border_date:
                            form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                            show_errors = 0
                            show_custom_date_error = 1
                        else:
                            form = TableForm(autosaloon_id, branch_id, hall_type, order_date, request.POST)
                            show_errors = 0
                            show_custom_date_error = 0
                    except ValueError:
                        form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                        show_errors = 1
                        show_custom_date_error = 0
                    except TypeError:
                        try:
                            time_structure = time.strptime(order_date_str, '%Y-%m-%d')
                            order_date = datetime(time_structure.tm_year, time_structure.tm_mon, time_structure.tm_mday)
                            border_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
                            if order_date < border_date:
                                form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                                show_errors = 0
                                show_custom_date_error = 1
                            else:
                                form = TableForm(autosaloon_id, branch_id, hall_type, order_date, request.POST)
                                show_errors = 0
                                show_custom_date_error = 0
                        except ValueError:
                            form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                            show_errors = 1
                            show_custom_date_error = 0
                else:
                    branch_id = request.POST.get('address')
                    hall_type = request.POST.get('hall')
                    order_date_str = request.POST.get('date')
                    try:
                        time_structure = time.strptime(order_date_str, '%Y-%m-%d')
                        order_date = datetime(time_structure.tm_year, time_structure.tm_mon, time_structure.tm_mday)
                        border_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
                        if order_date < border_date:
                            form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                        else:
                            form = TableForm(autosaloon_id, branch_id, hall_type, order_date, request.POST)
                    except ValueError:
                        form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                    except TypeError:
                        try:
                            time_structure = time.strptime(order_date_str, '%Y-%m-%d')
                            order_date = datetime(time_structure.tm_year, time_structure.tm_mon, time_structure.tm_mday)
                            border_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
                            if order_date < border_date:
                                form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                            else:
                                form = TableForm(autosaloon_id, branch_id, hall_type, order_date, request.POST)
                        except ValueError:
                            form = TableForm(autosaloon_id, branch_id, hall_type, -1, request.POST)
                    if form.is_valid():
                        # создание и запись в БД заказа
                        order_client_phone = form.cleaned_data['phone']
                        order_order_type = order_type
                        order_execute_date = form.cleaned_data['date']
                        order_execute_time = form.cleaned_data['time']
                        order_contact_account = Employee.objects.filter(
                            autosaloon__id=autosaloon_id
                        ).first()
                        order_branch_id = int(request.POST.get('address'))
                        order_autosaloon_branch = AutosaloonBranch.objects.filter(
                            id=order_branch_id
                        ).first()
                        order_table_seats = int(request.POST.get('table'))
                        order_hall_type = request.POST.get('hall')
                        order_dinner_wagon = DinnerWagon.objects.filter(
                            seats=order_table_seats,
                            hall__type=order_hall_type,
                            hall__branch=order_autosaloon_branch
                        ).first()
                        new_order = Order(
                            client_phone=order_client_phone,
                            type=order_order_type,
                            execute_date=order_execute_date,
                            execute_time=order_execute_time,
                            contact_account=order_contact_account,
                            autosaloon_branch=order_autosaloon_branch,
                            dinner_wagon=order_dinner_wagon
                        )
                        new_order.save()
                        for key in request.session.keys():
                            if key != 'cart_price':
                                row = OrdersCartRow(
                                    autosaloon_car=AutosaloonCar.objects.get(car__id=key),
                                    cares_count=request.session[key],
                                    order=new_order,
                                )
                                row.save()
                        new_order.make(type='table')
                        new_order.save(update_fields=['type', 'state'])

                        # удаление из сессии оформленных в заказе блюд и корзины, при необходимости
                        keys_for_delete = []
                        for key in request.session.keys():
                            if key != 'cart_price':
                                if autosaloon_cares.get(id=key) is not None:
                                    keys_for_delete.append(key)
                        for key in keys_for_delete:
                            del request.session[key]
                        is_cart_empty = True
                        for key in request.session.keys():
                            if key != 'cart_price':
                                is_cart_empty = False
                        if is_cart_empty:
                            del request.session['cart_price']

                        autosaloon = Autosaloon.objects.get(id=autosaloon_id)
                        return render(
                            request,
                            'orders/order_created.html',
                            {
                                'order_type': order_type,
                                'autosaloon_id': autosaloon_id,
                                'autosaloon_name': autosaloon.name,
                                'autosaloon_email': autosaloon.email,
                                'autosaloon_branch_order_phone': order_autosaloon_branch.order_phone_number,
                                'autosaloon_branch_help_phone': order_autosaloon_branch.help_phone_number
                            }
                        )
                    else:
                        show_errors = 1
                        show_custom_date_error = 0
            else:
                form = TableForm(autosaloon_id, -1, -1, -1)
                show_errors = 0
                show_custom_date_error = 0
            return render(
                request,
                'orders/make_order_form.html',
                {
                    # show_form определяет, нужно ли показывать форму пользователю
                    'show_form': 1,
                    'show_errors': show_errors,
                    'show_custom_date_error': show_custom_date_error,
                    'autosaloon_id': autosaloon_id,
                    'form': form,
                    'order_types_list': order_types,
                    'current_order_type': order_type
                }
            )
    else:
        show_errors = 0
        return render(
            request,
            'orders/make_order_form.html',
            {
                # show_form определяет, нужно ли показывать форму пользователю
                'show_form': 0,
                'show_errors': show_errors,
                'autosaloon_id': autosaloon_id
            }
        )


def get_user_form(request):
    """Возвращает на страницу форму для ввода номера телефона клиента"""
    if request.method == 'POST':
        form = UserOrdersForm(request.POST)
        if form.is_valid():
            is_phone_valid = 1
            user_orders = Order.objects.filter(client_phone=form.cleaned_data['phone'])
            current_datetime = datetime(
                datetime.now().year,
                datetime.now().month,
                datetime.now().day,
                datetime.now().hour,
                datetime.now().minute
            )
            for order in user_orders:
                order_execution_datetime = datetime(
                    order.execute_date.year,
                    order.execute_date.month,
                    order.execute_date.day,
                    order.execute_time.hour,
                    order.execute_time.minute
                )
                if order_execution_datetime <= current_datetime:
                    order.perform()
                    order.save(update_fields=['state'])
            return render(
                request,
                'orders/user_orders.html',
                {
                    'is_valid': is_phone_valid,
                    'form': form,
                    'orders': user_orders.order_by('-execute_date')
                }
            )
    else:
        form = UserOrdersForm()
    is_phone_valid = 0
    return render(
        request,
        'orders/user_orders.html',
        {
            'is_valid': is_phone_valid,
            'form': form
        }
    )


def view_order_car_list(request):
    if request.is_ajax():
        order_id = request.GET.get('id')
        order_rows = OrdersCartRow.objects.filter(order__id=order_id)
        cares_in_order = {}
        order_price = 0
        for row in order_rows:
            cares_in_order[row.autosaloon_car.car] = row.cares_count
            order_price += row.autosaloon_car.car.price * row.cares_count

        car_list = []
        for key, val in cares_in_order.items():
            car_specification = {'car_name': key.name, 'car_price': key.price, 'car_count': val}
            car_list.append(car_specification)
        order_info = {'order_price': order_price, 'order_components': car_list}

        json_string = json.dumps(order_info, ensure_ascii=False).encode('utf8')
        return HttpResponse(json_string)
    else:
        return HttpResponse('error')
