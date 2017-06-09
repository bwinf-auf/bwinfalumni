# BwInf Alumni Vereinssystem



## Installation

Für eine Testinstallation brauchen wir Python 3 und Django. Unter
Debian/Ubuntu heißt das:

    apt install python3 python3-django

Zuerst muss eine Datenbank angelegt werden und ein Account erstellt
werden

    cd bwinf-alumni
    python3 manage.py makemigrations benutzer mitglieder umsaetze # vorläufig
    python3 manage.py migrate            # Datenbank anlegen (sqlite)
    python3 manage.py createsuperuser    # Test-Admin erstellen 
    
Jetzt kann man der Server starten
    
    python3 manage.py runserver          # Server starten
    
Ein Webserver müsste jetzt auf Port 8000 lauschen.

Mit dem vorher angelegtem Admin-Account kann man sich jetzt unter
http://localhost:8000/admin anmelden.

TODO: Skript hinzufügen, dass zum Testen ein paar Pseudo-Daten in der
Datenbank anlegt.

## Funktionalität hinzufügen

Dafür bitte eine neue App erstellen und in INSTALLED_APPS eintragen 
(bwinfalumni/settings.py)

    python3 manage.py startapp <name>
    
Bestehende Apps als Referenz sind: `mitglieder`, `benutzer`, `umsaetze`.
    
Für alle weiteren Schritte, bitte die Django-Dokumentation zu rate
ziehen: https://docs.djangoproject.com/en/1.11/
