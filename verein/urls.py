from django.urls import path

from . import views

app_name = 'verein'
urlpatterns = [
    path("", views.index, name="index"),
]
