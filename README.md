# BWINF-Alumni und Freunde e.V. Vereinssystem

## Installation

Für eine Testinstallation brauchen wir Python 3 und Django. Unter
Debian/Ubuntu heißt das:

    apt install python3 python3-django

Nach dem checkout muss zunächst eine lokale Konfigurationsdatei mit
den Werten `DEBUG = True` und `SECRET_KEY` angelegt werden. Das geht
zum Beispiel mit:

    cd bwinfalumni
    printf "DEBUG = True\nSECRET_KEY='$(tr -dc A-Za-z0-9 </dev/urandom | head -c 50)'\n" >> bwinfalumni/settings_local.py

Dann muss eine Datenbank angelegt werden und ein Administrator-Account
erstellt werden

    ./manage.py migrate            # Datenbank anlegen (sqlite)
    ./manage.py createsuperuser    # Admin-Account erstellen

Jetzt kann man der Server starten

    ./manage.py runserver          # Server starten

Ein Webserver müsste jetzt auf Port 8000 lauschen.

Mit dem vorher angelegtem Admin-Account kann man sich jetzt unter
http://localhost:8000/admin anmelden.

## Testdaten erzeugen

Um ein paar Testdaten zu erzeugen, muss erst eine Django-Shell gestartet
werden

    ./manage.py shell

Dann kann man mithilfe des Pakets `mockverein` Testdaten erzeugen

    import mockverein
    mockverein.erstelle_mockdaten()

Dieses Skript kann nur einmal aufgerufen werden, da sonst versucht wird
doppelte Nutzer/Mitglieder zu erzeugen. Ggf. können diese aber mit 
`mockverein.loesche_nutzer()` wieder entfernt werden.

## Funktionalität hinzufügen

Dafür bitte eine neue App erstellen und in INSTALLED_APPS eintragen 
(bwinfalumni/settings.py)

    ./manage.py startapp <name>

Bestehende Apps als Referenz sind:
`benutzer`, `mitglieder`, `mitgliederverwaltung`, `mitgliedskonto`, `profil`, `umsaetze`.

Für alle weiteren Schritte, bitte die Django-Dokumentation zu rate
ziehen: https://docs.djangoproject.com/en/2.2/

