from django.conf.urls import url

from . import views

app_name = 'lastschriftmandatverwaltung'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.detail, name='detail'),
]
