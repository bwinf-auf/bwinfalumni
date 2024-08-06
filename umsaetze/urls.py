from django.conf.urls import url

from . import views

app_name = 'umsaetze'
urlpatterns = [
    url(r'^$', views.listumsaetze, name='index'),
    url(r'^kassenbuch/(?P<jahr>[0-9]+)/$', views.reportumsaetze, name='kassenbuch'),
    url(r'^kassenbuch/(?P<jahr>[0-9]+)/csv$', views.reportumsaetzecsv, name='kassenbuchcsv'),
    url(r'^bericht/(?P<jahr>[0-9]+)/$', views.report, name='bericht'),
    url(r'^bericht/(?P<jahr>[0-9]+)/csv$', views.reportcsv, name='berichtcsv'),
    url(r'^einzahlungen/$', views.einzahlungen, name='einzahlungen'),
]
