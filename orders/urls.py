from django.conf.urls import patterns, url
from orders import views

urlpatterns = patterns(
    '',

    url(r'cart/(?P<cart_state>\d+)/$', views.view_cart, name='cart'),

    url(r'cart/orders/$', views.view_orders, name='cart_orders'),

    # url for ajax
    url(r'cart/orders/car_list/$', views.view_autosaloon_car_list, name='cart_orders_autosaloon_car_list'),

    # url for ajax
    url(r'cart/increment_car/$', views.increment_car, name='cart_car_incrementation'),

    # url for ajax
    url(r'cart/decrement_car/$', views.decrement_car, name='cart_car_decrementation'),

    url(r'make_order/(?P<autosaloon_id>\d+)/(?P<order_type>\d+)/$', views.get_order_form, name='get_form'),

    url(r'my_orders/$', views.get_user_form, name='get_user_form'),

    # url for ajax
    url(r'my_orders/car_list/$', views.view_order_car_list, name='view_order_car_list')
)
