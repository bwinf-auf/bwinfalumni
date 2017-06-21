from django.db import models
from datetime import date



class UmsatzTyp(models.Model):
    
    typname             = models.CharField(max_length=200)
    beschreibung        = models.CharField(max_length=200)
    
    def __str__(self):
        return self.typname

    class Meta:
        db_table = "umsatztyp"
        verbose_name = "Umsatztyp"
        verbose_name_plural = "Umsatztypen"



class Konto(models.Model):
    
    kontoname           = models.CharField(max_length=200)
    beschreibung        = models.CharField(max_length=200)
    
    def __str__(self):
        return self.kontoname

    class Meta:
        db_table = "konto"
        verbose_name = "Konto"
        verbose_name_plural = "Konten"



class Umsatz(models.Model):
    
    konto               = models.ForeignKey(Konto, on_delete=models.PROTECT)
    typ                 = models.ForeignKey(UmsatzTyp, on_delete=models.PROTECT)
    text                = models.CharField(max_length=200)
    centWert            = models.IntegerField(default=0)
    quittung            = models.CharField(max_length=200)
    author              = models.CharField(max_length=200)
    geschaeftspartner   = models.CharField(max_length=200)
    wertstellungsdatum  = models.DateField(default=date.today)
    kommentar           = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return str(self.wertstellungsdatum)+ ": " + str(self.text) + " (" + str(self.typ) + ") " + str(self.centWert) + " ct"
    
    class Meta:
        db_table = "umsatz"
        verbose_name = "Umsatz"
        verbose_name_plural = "Umsätze"

