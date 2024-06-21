from django.urls import re_path as url

from . import views

app_name = 'profil'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sichtbarkeit/$', views.sichtbarkeit, name='sichtbarkeit'),
    url(r'^mitglieder/$', views.showallusers, name='mitgliederliste'),
    url(r'^(?P<mitgliedid>[0-9]+)/$', views.showuser, name='detail'),
]
