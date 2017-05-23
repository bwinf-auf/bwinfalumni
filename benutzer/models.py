from django.db import models
from django.contrib.auth.models import User
from mitglieder.models import Mitglied



class BenutzerMitglied(models.Model):
    
    benutzer    = models.OneToOneField(User, on_delete=models.PROTECT, primary_key=True)
    mitglied    = models.ForeignKey(Mitglied, on_delete=models.PROTECT, null=True)
    
    class Meta:
        verbose_name = "Benutzer-Mitglied-Relation"
        verbose_name_plural = "Benutzer-Mitglied-Relationen"
    
