from django.db import models
from datetime import date
from umsaetze.models import Umsatz



class Mitglied(models.Model):

    mitgliedsnummer = models.IntegerField(unique=True)
    antragsdatum    = models.DateField(default=date.today)
    beitrittsdatum  = models.DateField(null=True, blank=True, default=date.today)
    istBeigetreten  = models.BooleanField(default=True)
    austrittsdatum  = models.DateField(null=True, blank=True)
    istAusgetreten  = models.BooleanField(default=False)

    vorname         = models.CharField(max_length=200)
    nachname        = models.CharField(max_length=200)
    anrede          = models.CharField(max_length=200, blank=True)
    geburtsdatum    = models.DateField(default=date(1970,1,1))
    
    strasse         = models.CharField(max_length=200)
    adresszusatz    = models.CharField(max_length=200, blank=True)
    plz             = models.CharField(max_length=10) 
    stadt           = models.CharField(max_length=200)
    land            = models.CharField(max_length=200, default="Deutschland") 
    telefon         = models.CharField(max_length=200)
    email           = models.EmailField()
    beruf           = models.CharField(max_length=200, blank=True)
    
    studienort      = models.CharField(max_length=200, blank=True)
    studienfach     = models.CharField(max_length=200, blank=True)
    
    teileInfoWelt   = models.CharField(max_length=2000, blank=True)
    teileInfoAlumni = models.CharField(max_length=2000, blank=True)
    teileInfoBwinf  = models.CharField(max_length=2000, blank=True)
    kommentar       = models.CharField(max_length=2000, blank=True)
    anzahlMahnungen = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.mitgliedsnummer) + ": " + self.vorname + " " + self.nachname
    
    class Meta:
        db_table = "mitglied"
        verbose_name = "Mitglied"
        verbose_name_plural = "Mitglieder"



class MitgliedskontoBuchungstyp(models.Model):
    
    typname         = models.CharField(max_length=200)
    
    def __str__(self):
        return self.typname
    
    class Meta:
        db_table = "mitgliedskontoBuchungstyp"
        verbose_name = "Mitgliedskonto-Buchungstyp"
        verbose_name_plural = "Mitgliedskonto-Buchungstypen"



class MitgliedskontoBuchung(models.Model):
    
    mitglied        = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    typ             = models.ForeignKey(MitgliedskontoBuchungstyp, on_delete=models.PROTECT)
    centWert        = models.IntegerField(default=0)
    kommentar       = models.CharField(max_length=200, blank=True)
    umsatz          = models.ForeignKey(Umsatz, on_delete=models.PROTECT, blank=True, null=True)
    buchungsDatum   = models.DateField(default=date.today)
    
    def __str__(self):
        return str(self.buchungsDatum)+ " (" + str(self.typ) + ") " + str(self.centWert) + " ct"
    
    class Meta:
        db_table = "mitgliedskontoBuchung"
        verbose_name = "Mitgliedskonto-Buchung"
        verbose_name_plural = "Mitgliedskonto-Buchungen"



class Lastschriftmandat(models.Model):
    
    mitglied        = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    kontoinhaber    = models.CharField(max_length=200)
    bankname        = models.CharField(max_length=200)
    iban            = models.CharField(max_length=200)
    bic             = models.CharField(max_length=200)
    gueltigAb       = models.DateField(default=date.today)
    gueltigBis      = models.DateField(default=date(3000,1,1))

    class Meta:
        db_table = "lastschriftmandat"
        verbose_name = "Lastschriftmandat"
        verbose_name_plural = "Lastschriftmandate"
