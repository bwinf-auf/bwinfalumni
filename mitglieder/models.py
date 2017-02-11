from django.db import models
from datetime import date
from umsaetze.models import Umsatz

# Create your models here.

class Mitglied(models.Model):
    mitgliedsNummer = models.IntegerField(default=0, unique=True)
    name = models.CharField(max_length=200)
    beitrittsDatum = models.DateField(default=date.today) 
    austrittsDatum = models.DateField(default=date(3000,1,1))
    istAusgetreten = models.BooleanField(default=False)
    def __str__(self):
        return str(self.mitgliedsNummer) + ": " + self.name

class MitgliedskontoBuchungsTyp(models.Model):
    typname = models.CharField(max_length=200)
    def __str__(self):
        return self.typname
        
class MitgliedskontoBuchung(models.Model):
    mitglied = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    typ = models.ForeignKey(MitgliedskontoBuchungsTyp, on_delete=models.PROTECT)
    centValue = models.IntegerField(default=0)
    kommentar = models.CharField(max_length=200, blank=True)
    umsatz = models.ForeignKey(Umsatz, on_delete=models.PROTECT, blank=True, null=True)
    buchungsDatum = models.DateField(default=date.today)
    def __str__(self):
        return str(self.buchungsDatum)+ " (" + str(self.typ) + ") " + str(self.centValue) + " ct"
    
#class BeitragsTyp
#    name = models.CharField(max_length=200)
