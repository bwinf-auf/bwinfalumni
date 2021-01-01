from django.conf.urls import url

from . import views

app_name = 'mitgliederkarte'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
