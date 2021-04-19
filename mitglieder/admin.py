from django.contrib import admin

from .models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp

admin.site.register(Mitglied)
admin.site.register(MitgliedskontoBuchung)
admin.site.register(MitgliedskontoBuchungstyp)
