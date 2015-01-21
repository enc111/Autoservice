from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'Car_shop.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^cars/', include('Car.urls')),
                       url(r'^auth/', include('logsys.urls')),
                       url(r'^$', include('Car.urls')),
                       #url(r'^cart/', include('cart.urls'))
                        ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
