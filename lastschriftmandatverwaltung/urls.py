from django.urls import re_path as url

from . import views

app_name = 'lastschriftmandatverwaltung'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/neu$', views.addnew, name='addnew'),
    url(r'^delete/(?P<lastschriftmandat_id>[0-9]+)$', views.delete, name='delete'),
    url(r'^accept/(?P<lastschriftmandat_id>[0-9]+)$', views.accept, name='accept'),
]
