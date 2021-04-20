from django.shortcuts import render
from django.http import HttpResponse

from mitglieder.models import Mitglied

import csv
import datetime


def index(request):
    today = datetime.datetime.today()

    with open('listen/mitgliederliste', 'w', encoding='utf8') as f:
        ms = Mitglied.objects \
                    .filter(sichtbarkeit__bereich='alumni', sichtbarkeit__sache='mailingliste') \
                    .filter(beitrittsdatum__lte=today) \
                    .exclude(austrittsdatum__lte=today)

        for mitglied in ms:
            f.write(mitglied.email + "\n")

    with open('listen/ankuendigungenliste', 'w', encoding='utf8') as f:
        ms = Mitglied.objects \
                    .filter(beitrittsdatum__lte=today) \
                    .exclude(austrittsdatum__lte=today)

        for mitglied in ms:
            f.write(mitglied.email + "\n")

    with open('listen/bwinfadressen.csv', 'w', encoding='utf8', newline='') as f:
        ms = Mitglied.objects \
                    .filter(sichtbarkeit__bereich='bwinf', sichtbarkeit__sache='vorname') \
                    .filter(sichtbarkeit__bereich='bwinf', sichtbarkeit__sache='nachname') \
                    .filter(sichtbarkeit__bereich='bwinf', sichtbarkeit__sache='adresse') \
                    .filter(beitrittsdatum__lte=today) \
                    .exclude(austrittsdatum__lte=today)

        csvwriter = csv.writer(f)

        for mitglied in ms:
            csvwriter.writerow([mitglied.vorname,
                                mitglied.nachname,
                                mitglied.strasse,
                                mitglied.adresszusatz,
                                mitglied.plz,
                                mitglied.stadt,
                                mitglied.land])

    return HttpResponse("OK")
