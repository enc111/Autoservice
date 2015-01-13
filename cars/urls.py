from django.conf.urls import patterns, url
from cars import views
from cars.views import CarsList, CarAbout

urlpatterns = patterns(
    '',

    url(r'(?P<autosaloon_id>\d+)/$', CarsList.as_view(), name='cars_without_category'),

    url(r'(?P<autosaloon_id>\d+)/(?P<car_category>\d+)?', CarsList.as_view(), name='cars_with_category'),

    url(r'car/(?P<car_id>\d+)/?', CarAbout.as_view(), name='car_about'),

    # url for ajax requests
    url(r'update_cart/$', views.add_car, name='cart_updating'),

    # url for ajax requests
    url(r'load_cart/$', views.load_cart, name='cart_loading'),
)
