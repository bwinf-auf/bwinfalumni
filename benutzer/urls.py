from django.conf.urls import url

from . import views

app_name = 'benutzer'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^alle/$', views.listusers, name='benutzerliste'),
    url(r'^(?P<userid>[0-9]+)/$', views.showuser, name='detail'),
    url(r'^add/$', views.addbenutzer, name='add'),
    url(r'^add/(?P<mitgliedsnummer>[0-9]+)/$', views.addbenutzer, name='addmitgliedsnummer'),
]
