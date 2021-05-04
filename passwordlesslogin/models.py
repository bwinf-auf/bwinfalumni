from django.db import models

from mitglieder.models import Mitglied


class Passwordlesslogincode(models.Model):

    benutzer    = models.ForeignKey(Mitglied, on_delete=models.PROTECT)
    logincode   = models.CharField(max_length=250)
    valid_until = models.DateField()
