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
            mitgliedsnummer = int(username)
        except:
            return None

        try:
            mitglied = Mitglied.objects.get(mitgliedsnummer=mitgliedsnummer)
            for benutzermitglied in mitglied.benutzermitglied_set.all():
                user = benutzermitglied.benutzer
                if check_password(password, user.password) and self.user_can_authenticate(user):
                    return user
            return None
        except User.DoesNotExist:
            return None
        return None


class MitgliedEmailBackend(ModelBackend):
    """
    Authentifiziert gegen die Mitglied-E-Mailadresse (und Passwort) statt gegen
    den Benutzernamen.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            for mitglied in Mitglied.objects.filter(email = username):
                for benutzermitglied in mitglied.benutzermitglied_set.all():
                    user = benutzermitglied.benutzer
                    if check_password(password, user.password) and self.user_can_authenticate(user):
                        return user
            return None
        except User.DoesNotExist:
            return None
        return None


class EmailBackend(ModelBackend):
    """
    Authentifiziert gegen die Account-E-Mailadresse (und Passwort) statt gegen
    den Benutzernamen.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        for user in User.objects.filter(email=username):
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
