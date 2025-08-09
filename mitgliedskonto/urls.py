from django.urls import re_path as url

from . import views

app_name = 'mitgliedskonto'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/(?P<mitgliedskontobuchungsnummer>[0-9]+)/$', views.bescheinigung, name='bescheinigung'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/(?P<mitgliedskontobuchungsnummer>[0-9]+)/create$', views.bescheinigung_erstellen, name='bescheinigung_erstellen'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/(?P<mitgliedskontobuchungsnummer>[0-9]+)/verify$', views.bescheinigung_verifizieren, name='bescheinigung_verifizieren'),
    url(r'^beitraege/$', views.beitraegeeinziehen, name='beitraege'),
    url(r'^beitraege/mailversand/(?P<templatename>\w+)/$', views.zahlungsaufforderungen, {'schulden': False}, name='beitragsmails'),
    url(r'^beitraege/mailversand/(?P<templatename>\w+)/schulden/$', views.zahlungsaufforderungen, {'schulden': True}, name='beitragsmailsschulden'),
    url(r'^add/$', views.addmitglied, name='add'),
]
