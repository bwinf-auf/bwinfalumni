from django.db import models

from mitglieder.models import Mitglied

from datetime import date


class GekuerztesLastschriftmandat(models.Model):

    mitglied     = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    kontoinhaber = models.CharField(max_length=250)
    anschrift    = models.CharField(max_length=500)
    bankname     = models.CharField(max_length=250)
    iban         = models.CharField(max_length=250)
    bic          = models.CharField(max_length=250)
    referenz     = models.CharField(max_length=250)
    erstellung   = models.DateField(default=date.today)
    unterschrift = models.DateField(null=True,default=None)
    bestaetigung = models.DateField(null=True,default=None)
    gueltig_ab   = models.DateField(null=True,default=None)
    gueltig_bis  = models.DateField(null=True,default=None)

    def __str__(self):
        ab = "noch nicht gültig" if self.gueltig_ab == None or self.gueltig_ab > date.today() else "GÜLTIG"
        bis = ab if self.gueltig_bis == None or self.gueltig_bis > date.today() else "nicht mehr gültig"

        return str(self.kontoinhaber) + ": " + self.iban + ", " + self.bic + " (" + bis + ": " + str(self.gueltig_ab) + " – " + str(self.gueltig_bis) + ")"

    class Meta:
        db_table = "gek_lastschriftmandat"
        verbose_name = "Gekürztes Lastschriftmandat"
        verbose_name_plural = "Gekürzte Lastschriftmandate"
