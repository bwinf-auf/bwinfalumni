#from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from mitglieder.models import Mitglied

class MitgliedsnummerBackend:
    """
    Authentifiziert gegen die Mitgliedsnummer (und Passwort) statt gegen
    den Benutzernamen.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            if username[0] == "m":
                username = username[1:]
            userid = int(username)
        except:
            return None ## Oder sollte das einen Fehler werfen?
        
        try:
            mitglied = Mitglied.objects.get(mitgliedsnummer = userid)
            user = mitglied.benutzermitglied_set.first().benutzer
            if check_password(password, user.password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None
            # Hier könnte ein Benutzer angelegt werden. TODO: Wie?
            user = User(username=username)
            user.save()

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
