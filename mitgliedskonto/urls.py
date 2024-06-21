from django.urls import re_path as url

from . import views

app_name = 'mitgliedskonto'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<mitgliedsnummer>[0-9]+)/$', views.detail, name='detail'),
    url(r'^beitraege/$', views.beitraegeeinziehen, name='beitraege'),
    url(r'^beitraege/mailversand/(?P<templatename>\w+)/$', views.zahlungsaufforderungen, {'schulden': False}, name='beitragsmails'),
    url(r'^beitraege/mailversand/(?P<templatename>\w+)/schulden/$', views.zahlungsaufforderungen, {'schulden': True}, name='beitragsmailsschulden'),
    url(r'^add/$', views.addmitglied, name='add'),
]
