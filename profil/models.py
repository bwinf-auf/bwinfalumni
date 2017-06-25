from django.db import models
from mitglieder.models import Mitglied


class Sichtbarkeit(models.Model):
    mitglied = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    bereich  = models.CharField(max_length=200)
    sache    = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.mitglied.mitgliedsnummer)+ " (" + str(self.bereich) + "): " + str(self.sache)
    
    class Meta:
        db_table = "sichtbarkeit"
        verbose_name = "Sichtbarkeit"
        verbose_name_plural = "Sichtbarkeiten"
