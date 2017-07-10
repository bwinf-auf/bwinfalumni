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

urlpatterns = [
    url(r'^umsaetze/', include('umsaetze.urls', namespace='umsaetze')),
    url(r'^mitglieder/', include('mitglieder.urls', namespace='mitglieder')),
    url(r'^benutzer/', include('benutzer.urls', namespace='benutzer')),
    url(r'^profil/', include('profil.urls', namespace='profil')),
    url(r'^mailinglistenadressen/', include('mailinglistenadressen.urls', namespace='mailinglistenadressen')),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', { 'template_name': 'registration/logout.html',}, name='logout' ),
    url(r'^accounts/resetpassword/passwordsent/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^accounts/resetpassword/passwordchanged/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^accounss/reset/done/$', 'django.contrib.auth.views.password_change_done', name='password_reset_complete'),
    url(r'^admin/', admin.site.urls),
]



admin.site.site_header = 'BwInf-Alumni Login'

