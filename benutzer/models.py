from django.db import models
from django.contrib.auth.models import User
from mitglieder.models import Mitglied



class BenutzerMitglied(models.Model):

    benutzer    = models.OneToOneField(User, on_delete=models.PROTECT, primary_key=True)
    mitglied    = models.ForeignKey(Mitglied, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.benutzer) + " – " + str(self.mitglied)

    class Meta:
        db_table = "benutzer_mitglied_relation"
        verbose_name = "Benutzer-Mitglied-Relation"
        verbose_name_plural = "Benutzer-Mitglied-Relationen"
