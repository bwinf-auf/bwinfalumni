# BwInf Alumni Vereinssystem



## Installation

Für eine Testinstallation brauchen wir Python 3 und Django. Unter
Debian/Ubuntu heißt das:

    apt install python3 python3-django

Zuerst muss eine Datenbank angelegt werden und ein Account erstellt
werden

    cd bwinf-alumni
    ./manage.py migrate            # Datenbank anlegen (sqlite)
    ./manage.py createsuperuser    # Test-Admin erstellen 
    
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

