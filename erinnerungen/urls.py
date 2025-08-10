from django.urls import path

from . import views

app_name = 'erinnerungen'
urlpatterns = [
    path("", views.index, name="index"),
    path("nudge", views.nudge, name="nudge"),
]
