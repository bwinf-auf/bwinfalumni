from django.urls import re_path as url

from . import views

app_name = 'dringendes'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
