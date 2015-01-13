from django.conf.urls import patterns, url
from autosaloons import views
from autosaloons.views import AutosaloonsList

urlpatterns = patterns(
    '',

    url(r'^$', AutosaloonsList.as_view(), name='home'),

    url(r'(?P<city_id>\d+)/$', AutosaloonsList.as_view(), name='autosaloons'),

    # url for ajax requests
    url(r'flush_session/$', views.delete_expired_session_data, name='session_cleaning'),

    url(r'^about/$', views.about_page_view, name='about_page'),
)
