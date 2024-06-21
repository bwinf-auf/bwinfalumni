from django.urls import re_path as url

from . import views

app_name = 'mitgliederkarte'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
