from django.db import models
from datetime import date



class UmsatzTyp(models.Model):
    
    typname             = models.CharField(max_length=200)
    
    def __str__(self):
        return self.typname

    class Meta:
        verbose_name = "Umsatztyp"
        verbose_name_plural = "Umsatztypen"



class Umsatz(models.Model):
    
    typ                 = models.ForeignKey(UmsatzTyp, on_delete=models.PROTECT)
    text                = models.CharField(max_length=200)
    centWert            = models.IntegerField(default=0)
    wertstellungsdatum  = models.DateField(default=date.today)
    
    def __str__(self):
        return str(self.wertstellungsdatum)+ ": " + str(self.text) + " (" + str(self.typ) + ") " + str(self.centWert) + " ct"
    
    class Meta:
        verbose_name = "Umsatz"
        verbose_name_plural = "Umsätze"

