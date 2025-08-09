from django.db import models
from datetime import date

class Verein(models.Model):

    mitgliedsbeitrag_cent = models.IntegerField(null=True, blank=True)
    vorstand1             = models.CharField(max_length=250, blank=True)
    vorstand2             = models.CharField(max_length=250, blank=True)
    beschlussfassung      = models.DateField(default=date.today)

    def __str__(self):
        return (("Mitgliedsbeitrag: " + str(self.mitgliedsbeitrag_cent / 100.0)) if self.mitgliedsbeitrag_cent != None else "") + ", Beschlussfassung: " + str(self.beschlussfassung)

    class Meta:
        db_table = "verein"
        verbose_name = "Verein"
        verbose_name_plural = "Vereinsbeschlüsse"

class Freistellungsbescheid(models.Model):

    finanzamt    = models.CharField(max_length=250)
    steuernummer = models.CharField(max_length=250)
    zeitraum     = models.CharField(max_length=250)
    datum        = models.DateField(default=date.today)

    def __str__(self):
        return "Freistellungsbescheid vom Finanzamt " + finanzamt + " (Steuernummer" + self.steuernummer + ") für den Zeitraum " + self.zeitraum + " wurde erteilt am " + str(self.datum) + "."

    class Meta:
        db_table = "freistellungsbescheid"
        verbose_name = "Freistellungsbescheid"
        verbose_name_plural = "Freistellungsbescheide"
