from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'Car_shop.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^all/', 'Car.views.car_all'),
                       url(r'^get/(?P<car_id>\d+)/$', 'Car.views.car'),
                       url(r'add_comments/(?P<car_id>\d+)/$', 'Car.views.add_comments', name='add_comment'),
                       url(r'^shop_inf/', 'Car.views.shop_inf'),
                       url(r'^$', 'Car.views.car_all'),
                       url(r'^load_cart/$', 'Car.views.load_cart', name='cart_loading'),
                       url(r'^update_cart/$', 'Car.views.add_car', name='cart_updating'),

)