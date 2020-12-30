"""bwinfalumni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^umsaetze/', include('umsaetze.urls', namespace='umsaetze')),
    url(r'^profil/', include('profil.urls', namespace='profil')),
    url(r'^verwaltung/', include('mitgliederverwaltung.urls', namespace='mitgliederverwaltung')),
    url(r'^konto/', include('mitgliedskonto.urls', namespace='mitgliedskonto')),
    url(r'^mailinglistenadressen/', include('mailinglistenadressen.urls', namespace='mailinglistenadressen')),
    url(r'^mitgliederkarte/', include('mitgliederkarte.urls', namespace='mitgliederkarte')),
    url(r'^lastschriftmandate/', include('lastschriftmandatverwaltung.urls', namespace='lastschriftmandatverwaltung')),

    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), { 'template_name': 'registration/logout.html',}, name='logout' ),
    url(r'^accounts/resetpassword/passwordsent/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^accounts/resetpassword/passwordchanged/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^accounts/', include(('django.contrib.auth.urls','auth'), namespace='auth')),
    url(r'^accounts/reset/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_reset_complete'),
    url(r'^admin/', admin.site.urls),
]



admin.site.site_header = 'BwInf-Alumni Login'

