from django.conf.urls import url

from . import views

app_name = 'emailbenutzername'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^benutzername$', views.benutzername, name='benutzername'),
    url(r'^email$', views.email, name='email'),
]
