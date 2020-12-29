from django.conf.urls import include, url

from . import views

app_name = 'mitgliederverwaltung'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^alle/$', views.listusers, name='benutzerliste'),
    url(r'^(?P<userid>[0-9]+)/$', views.showuser, name='detail'),
    url(r'^add/$', views.addbenutzer, name='add'),
    url(r'^add/(?P<mitgliedsnummer>[0-9]+)/$', views.addbenutzer, name='addmitgliedsnummer'),
    url(r'^kontostatistik/', include('kontostatistik.urls', namespace='kontostatistik')),
]
