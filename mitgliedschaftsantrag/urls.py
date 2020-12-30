from django.conf.urls import url

from . import views

app_name = 'mitgliedschaftsantrag'

urlpatterns = [
    url(r'^$', views.antrag, name='antrag'),
]
