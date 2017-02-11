from django.contrib import admin

# Register your models here.

from .models import Umsatz, UmsatzTyp
admin.site.register(Umsatz)
admin.site.register(UmsatzTyp)
