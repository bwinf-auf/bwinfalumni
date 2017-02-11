from django.conf.urls import url

from . import views

app_name = 'mitglieder'
urlpatterns = [
    url(r'^$', views.mitglieder, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.mitglied, name='detail'),
    url(r'^add/$', views.addmitglied, name='add'),
]
