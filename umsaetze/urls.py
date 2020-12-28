from django.conf.urls import url

from . import views

app_name = 'umsaetze'
urlpatterns = [
    url(r'^$', views.listumsaetze, name='index'),
    url(r'^einzahlungen/$', views.einzahlungen, name='einzahlungen'),
]

