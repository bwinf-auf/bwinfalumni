from django.db import models

from mitglieder.models import Mitglied

from datetime import date


class GekuerztesLastschriftmandat(models.Model):
    
    mitglied     = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    kontoinhaber = models.CharField(max_length=250)
    bankname     = models.CharField(max_length=250)
    iban         = models.CharField(max_length=250)
    bic          = models.CharField(max_length=250)
    referenz     = models.CharField(max_length=250)
    erstellung   = models.DateField(default=date.today)
    unterschrift = models.DateField(null=True,default=None)
    bestaetigung = models.DateField(null=True,default=None)
    gueltig_ab   = models.DateField(null=True,default=None)
    gueltig_bis  = models.DateField(null=True,default=None)

    class Meta:
        db_table = "gek_lastschriftmandat"
        verbose_name = "Gekürztes Lastschriftmandat"
        verbose_name_plural = "Gekürzte Lastschriftmandate"
