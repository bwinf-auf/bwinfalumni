from django.contrib import admin

from .models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp, Lastschriftmandat

admin.site.register(Mitglied)
admin.site.register(MitgliedskontoBuchung)
admin.site.register(MitgliedskontoBuchungstyp)
admin.site.register(Lastschriftmandat)
