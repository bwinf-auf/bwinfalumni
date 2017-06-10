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
    url(r'^umsaetze/', include('umsaetze.urls')),
    url(r'^mitglieder/', include('mitglieder.urls')),
    url(r'^benutzer/', include('benutzer.urls')),
    url(r'^mock/', include('mockverein.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', admin.site.urls),
]

admin.site.site_header = 'BwInf-Alumni Login'
