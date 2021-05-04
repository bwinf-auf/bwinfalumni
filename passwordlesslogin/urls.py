from django.conf.urls import url

from . import views

app_name = 'passwordlesslogin'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logincode/(?P<code>[-a-zA-Z0-9_]+)$', views.verifikation, name='verifikationparam'),
]
