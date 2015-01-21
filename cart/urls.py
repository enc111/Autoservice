from django.conf.urls import patterns, url


urlpatterns = patterns('Car_shop.cart.views',
                       # Examples:
                       # url(r'^$', 'Car_shop.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                      url(r'^$', 'show_cart', { 'template_name' : 'cart/shoppingcart.html'}, 'show_cart'),

)