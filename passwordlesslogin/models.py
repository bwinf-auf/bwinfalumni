from django.db import models

from django.contrib.auth.models import User

class Passwordlesslogincode(models.Model):
    benutzer    = models.ForeignKey(User, on_delete=models.PROTECT)
    logincode   = models.CharField(max_length=250)
    valid_until = models.DateTimeField()
