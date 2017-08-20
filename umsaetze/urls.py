from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.listumsaetze, name='index'),
    url(r'^einzahlungen/$', views.einzahlungen, name='einzahlungen'),
]

