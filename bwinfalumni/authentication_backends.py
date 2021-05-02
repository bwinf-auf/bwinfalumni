#from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from mitglieder.models import Mitglied

class MitgliedsnummerBackend(ModelBackend):
    """
    Authentifiziert gegen die Mitgliedsnummer (und Passwort) statt gegen
    den Benutzernamen.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if username[0] == "m":
                username = username[1:]
            userid = int(username)
        except:
            return None

        try:
            mitglied = Mitglied.objects.get(mitgliedsnummer = userid)
            for benutzermitglied in mitglied.benutzermitglied_set.all():
                user = benutzermitglied.benutzer
                if check_password(password, user.password):
                    return user
            return None
        except User.DoesNotExist:
            return None
