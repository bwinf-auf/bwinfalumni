from django.db import models
from django.contrib.auth.models import User
from mitglieder.models import Mitglied

# Create your models here.


class BenutzerInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, primary_key=True)
    mitglied = models.ForeignKey(Mitglied, on_delete=models.PROTECT, null=True)
    
