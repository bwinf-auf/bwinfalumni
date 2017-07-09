from django.conf.urls import url

from . import views

app_name = 'mitglieder'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.detail, name='detail'),
    url(r'^add/$', views.addmitglied, name='add'),
]
