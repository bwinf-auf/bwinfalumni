from django.contrib import admin

# Register your models here.
from .models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungsTyp
admin.site.register(Mitglied)
admin.site.register(MitgliedskontoBuchung)
admin.site.register(MitgliedskontoBuchungsTyp)
