from django.db import models
from datetime import date
from umsaetze.models import Umsatz



class Mitglied(models.Model):

    mitgliedsnummer = models.IntegerField(unique=True)
    antragsdatum    = models.DateField(default=date.today)
    beitrittsdatum  = models.DateField(null=True, blank=True)
    austrittsdatum  = models.DateField(null=True, blank=True)
    beitrag_cent    = models.IntegerField(default=1000)
    foerdermitglied = models.BooleanField(default=False)

    vorname         = models.CharField(max_length=250)
    nachname        = models.CharField(max_length=250)
    anrede          = models.CharField(max_length=250, blank=True)
    geburtsdatum    = models.DateField(default=date(1970,1,1))

    strasse         = models.CharField(max_length=250)
    adresszusatz    = models.CharField(max_length=250, blank=True)
    plz             = models.CharField(max_length=10)
    stadt           = models.CharField(max_length=250)
    land            = models.CharField(max_length=250, default="Deutschland")
    telefon         = models.CharField(max_length=250, blank=True)
    email           = models.EmailField()
    beruf           = models.CharField(max_length=250, blank=True)

    studienort      = models.CharField(max_length=250, blank=True)
    studienfach     = models.CharField(max_length=250, blank=True)

    kommentar       = models.CharField(max_length=2000, blank=True)
    anzahl_mahnungen = models.IntegerField(default=0)

    def __str__(self):
        ab = "noch kein Mitglied" if self.beitrittsdatum == None or self.beitrittsdatum > date.today() else "MITGLIED"
        bis = ab if self.austrittsdatum == None or self.austrittsdatum > date.today() else "kein Mitglied mehr"

        return str(self.mitgliedsnummer) + ": " + self.vorname + " " + self.nachname + " (" + bis + ": " + str(self.beitrittsdatum) + " – " + str(self.austrittsdatum) + ")"


    def aktiv(self):
        #Ist Aktiv, falls Beitrittsdatum <= today < Austrittsdatum
        if self.beitrittsdatum is None:
            return False

        if self.beitrittsdatum > date.today():
            return False

        if self.austrittsdatum is None:
            return True

        if self.austrittsdatum <= date.today():
            return False

        return True

    class Meta:
        db_table = "mitglied"
        verbose_name = "Mitglied"
        verbose_name_plural = "Mitglieder"
        ordering = ('mitgliedsnummer',)





class MitgliedskontoBuchungstyp(models.Model):

    typname         = models.CharField(max_length=250)

    def __str__(self):
        return self.typname

    class Meta:
        db_table = "mitgliedskonto_buchungstyp"
        verbose_name = "Mitgliedskonto-Buchungstyp"
        verbose_name_plural = "Mitgliedskonto-Buchungstypen"



class MitgliedskontoBuchung(models.Model):

    mitglied        = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    typ             = models.ForeignKey(MitgliedskontoBuchungstyp, on_delete=models.PROTECT)
    cent_wert       = models.IntegerField(default=0)
    kommentar       = models.CharField(max_length=250, blank=True)
    umsatz          = models.ForeignKey(Umsatz, on_delete=models.PROTECT, blank=True, null=True)
    buchungsdatum   = models.DateField(default=date.today)
    wirksam         = models.BooleanField(default=True) # Spenden sind nichtwirksame Buchungen auf dem Mitgliedskonto

    def __str__(self):
        return str(self.buchungsdatum)+ " (" + str(self.typ) + ") " + str(self.cent_wert) + " ct"

    class Meta:
        db_table = "mitgliedskonto_buchung"
        verbose_name = "Mitgliedskonto-Buchung"
        verbose_name_plural = "Mitgliedskonto-Buchungen"
