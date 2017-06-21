from django.conf.urls import url

from . import views

app_name = 'bootstrap_from_old_database'
urlpatterns = [
    url(r'^$', views.bootstrap, name='index'),
]
