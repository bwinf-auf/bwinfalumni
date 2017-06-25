from django.conf.urls import url

from . import views

app_name = 'profil'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^sichtbarkeit/$', views.sichtbarkeit, name='sichtbarkeit'),
    #url(r'^(?P<userid>[0-9]+)/$', views.showuser, name='detail'),
]
