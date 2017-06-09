from django.contrib import admin

# Register your models here.

from .models import Umsatz, UmsatzTyp, Konto
admin.site.register(Umsatz)
admin.site.register(UmsatzTyp)
admin.site.register(Konto)
