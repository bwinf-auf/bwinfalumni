from django.conf.urls import url

from . import views

app_name = 'mitgliedschaftsantrag'

urlpatterns = [
    url(r'^$', views.neuerantrag, name='neuerantrag'),
    url(r'^verifiziere/$', views.verifikation, name='verifikation'),
    url(r'^verifiziere/(?P<code>[-a-zA-Z0-9_]+)$', views.verifikation, name='verifikationparam'),
    url(r'^abschluss/(?P<mitgliedsnummer>[0-9]+)/$', views.zahlungsinformationen, name='zahlungsinformationen'),
    url(r'^antrag/(?P<mitgliedsnummer>[0-9]+)/$', views.antrag, name='antrag'),
]
