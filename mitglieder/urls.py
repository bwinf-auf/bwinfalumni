from django.conf.urls import url

from . import views

app_name = 'mitglieder'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.detail, name='detail'),
    url(r'^add/$', views.addmitglied, name='add'),
    url(r'^beitraege/$', views.beitraegeeinziehen, name='beitraege'),
    url(r'^beitraege/mailversand/(?P<template>\w+)/$', views.zahlungsaufforderungen, {'schulden': False}, name='beitragsmails'),
    url(r'^beitraege/mailversand/(?P<template>\w+)/schulden/$', views.zahlungsaufforderungen, {'schulden': True}, name='beitragsmailsschulden'),
]
