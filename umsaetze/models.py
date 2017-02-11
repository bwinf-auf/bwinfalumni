from django.db import models
from datetime import date
# Create your models here.



class UmsatzTyp(models.Model):
    typname = models.CharField(max_length=200)
    def __str__(self):
        return self.typname


class Umsatz(models.Model):
    typ = models.ForeignKey(UmsatzTyp, on_delete=models.PROTECT)
    text = models.CharField(max_length=200)
    centValue = models.IntegerField(default=0)
    wertstellungsDatum = models.DateField(default=date.today)
    def __str__(self):
        return str(self.wertstellungsDatum)+ ": " + str(self.text) + " (" + str(self.typ) + ") " + str(self.centValue) + " ct"

