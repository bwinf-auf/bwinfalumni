from django.db import models
from datetime import date

class Dauer(models.TextChoices):
    ZWEIJAHR  = "2Y", "Zweijährig"
    JAHR      = "Y", "Jährlich"
    HALBJAHR  = "HY", "Halbjährlich"
    QUARTAL   = "QY", "Quartalsweise"
    MONAT     = "M", "Monatlich"
    VIERWOCHE = "4W", "Vierwöchig"

class Erinnerung(models.Model):
    name     = models.CharField(max_length=250)
    titel    = models.CharField(max_length=250)
    erstmals = models.DateField(default=date.today)
    zuletzt  = models.DateField(default=date.today)
    zyklus   = models.CharField(max_length=2,
                                choices=Dauer.choices,
                                default=Dauer.JAHR)

    def __str__(self):
        return self.name + " (" + self.zyklus + ": " + str(self.zuletzt) + ")"

    class Meta:
        db_table = "erinnerung"
        verbose_name = "Erinnerung"
        verbose_name_plural = "Erinnerungen"
