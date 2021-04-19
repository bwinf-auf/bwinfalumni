from django.db import models
from datetime import date

class Mitgliedschaftsantrag(models.Model):

    MS_ARTEN = [
        ('O', 'Ordentliches Mitglied'),
        ('F', 'Fördermitglied'),
    ]

    mitgliedschaft    = models.CharField(max_length=2, choices=MS_ARTEN, default='O')
    mitgliedsbeitrag  = models.IntegerField(default=50)
    antragsdatum      = models.DateField(default=date.today)

    vorname           = models.CharField(max_length=250)
    nachname          = models.CharField(max_length=250)
    anrede            = models.CharField(max_length=250, blank=True)
    geburtsdatum      = models.DateField()

    strasse           = models.CharField(max_length=250)
    adresszusatz      = models.CharField(max_length=250, blank=True)
    plz               = models.CharField(max_length=10)
    stadt             = models.CharField(max_length=250)
    land              = models.CharField(max_length=250, default="Deutschland")
    telefon           = models.CharField(max_length=250, blank=True)
    email             = models.EmailField()
    verifikationscode = models.CharField(max_length=250)
    beruf             = models.CharField(max_length=250, blank=True)

    studienort        = models.CharField(max_length=250, blank=True)
    studienfach       = models.CharField(max_length=250, blank=True)

    mailingliste      = models.BooleanField()
    adresse_verein    = models.BooleanField()
    adresse_bwinf     = models.BooleanField()
    name_welt         = models.BooleanField()

    def __str__(self):
        return str(self.antragsdatum)+ ": " + self.vorname + " " + self.nachname + " (" + self.verifikationscode + "), Beitrag " + str(self.mitgliedsbeitrag) + " Euro"

    class Meta:
        db_table = "mitgliedschaftsantrag"
        verbose_name = "Mitgliedschaftsantrag"
        verbose_name_plural = "Mitgliedschaftsanträge"
