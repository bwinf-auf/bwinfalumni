from django.urls import re_path as url

from . import views

app_name = 'kontostatistik'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
