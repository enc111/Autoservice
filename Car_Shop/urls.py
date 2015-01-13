from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = patterns(
    '',

    # редирект с корня сайта на страницу выбора заведения для города
    url(r'^$', RedirectView.as_view(url=r'city/'), name="home_page"),

    # редирект на файл urls в приложении autosaloons
    url(r'^city/', include('autosaloons.urls')),

    # редирект на файл urls в приложении autosaloons
    url(r'^autosaloon/', include('cars.urls')),

    # редирект на файл urls в приложении orders
    url(r'^order/', include('orders.urls')),

    # страница пользователя организации
    url(r'^employee/', include('employees.urls')),

    # админка сайта
    url(r'^admin/', include(admin.site.urls)),
)
