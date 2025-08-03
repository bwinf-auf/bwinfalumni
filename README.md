# BWINF-Alumni und Freunde e.V. Vereinssystem

## Installation

Für eine Entwicklungsumgebung brauchen wir Python 3 und Django. Wir empfehlen `uv` ([Installation](https://docs.astral.sh/uv/getting-started/installation/)) zu nutzen:

    uv sync

Alternativ kann Django unter Debian stable von den Paketquellen installiert werden:

    apt install python3 python3-django

Zum Ausführen muss zunächst eine lokale Konfigurationsdatei mit
den Werten `DEBUG = True` und `SECRET_KEY` angelegt werden. Das geht
zum Beispiel mit:

    printf "DEBUG = True\nSECRET_KEY='$(tr -dc A-Za-z0-9 </dev/urandom \
            | head -c 50)'\n" >> bwinfalumni/settings_local.py

Dann muss eine Datenbank angelegt werden und ein Administrator-Account
erstellt werden

    uv run manage.py migrate
    uv run manage.py createsuperuser

(Wenn `uv` nicht verwendet wird, einfach statt `uv run manage.py` einfach direkt `./manage.py` nutzten!)

Jetzt kann man den Server starten

    uv run manage.py runserver

Ein Webserver lauscht jetzt auf Port 8000.

Mit dem vorher angelegtem Admin-Account kann man sich jetzt unter
http://localhost:8000/admin anmelden.

## Testdaten erzeugen

Um ein paar Testdaten zu erzeugen, muss erst eine Django-Shell gestartet
werden

    uv run manage.py shell

Dann kann man mithilfe des Pakets `mockverein` Testdaten erzeugen

    import mockverein
    mockverein.erstelle_mockdaten()

Dieses Skript kann nur einmal aufgerufen werden, da sonst versucht wird
doppelte Nutzer/Mitglieder zu erzeugen. Ggf. können diese aber mit 
`mockverein.loesche_nutzer()` wieder entfernt werden.

TODO: Das sollte auch noch in ein `manage.py`-Command umgewandelt werden und idempotent gemacht werden!

## Funktionalität hinzufügen

Dafür bitte eine neue App erstellen und in INSTALLED_APPS eintragen 
(bwinfalumni/settings.py)

    uv run manage.py startapp <name>

Bestehende Apps als Referenz sind:
`benutzer`, `mitglieder`, `mitgliederverwaltung`, `mitgliedskonto`, `profil`, `umsaetze`.

Für alle weiteren Schritte, bitte die Django-Dokumentation zu rate
ziehen: https://docs.djangoproject.com/en/3.2/

