from django.shortcuts import render
from mitglieder.models import Mitglied
from django.http import HttpResponse
import datetime

def index(request):
    today = datetime.datetime.today()
    
    with open('listen/mitgliederliste', 'w', encoding='utf8') as f:
    
        m = Mitglied.objects \
                    .filter(sichtbarkeit__bereich='alumni', sichtbarkeit__sache='mailingliste') \
                    .filter(beitrittsdatum__lte=today) \
                    .exclude(austrittsdatum__lte=today)
            
        for mitglied in m:
            f.write(mitglied.email + "\n")
            
    with open('listen/ankuendigungenliste', 'w', encoding='utf8') as f:
    
        m = Mitglied.objects \
                    .filter(beitrittsdatum__lte=today) \
                    .exclude(austrittsdatum__lte=today)
            
        for mitglied in m:
            f.write(mitglied.email + "\n")
    
    with open('listen/bwinfadressen', 'w', encoding='utf8') as f:
    
        m = Mitglied.objects \
                    .filter(sichtbarkeit__bereich='bwinf', sichtbarkeit__sache='vorname') \
                    .filter(sichtbarkeit__bereich='bwinf', sichtbarkeit__sache='nachname') \
                    .filter(sichtbarkeit__bereich='bwinf', sichtbarkeit__sache='adresse') \
                    .filter(beitrittsdatum__lte=today) \
                    .exclude(austrittsdatum__lte=today)
            
        for mitglied in m:
            f.write(mitglied.vorname + "," \
                + mitglied.nachname + "," \
                + mitglied.strasse + "," \
                + mitglied.adresszusatz + "," \
                + mitglied.plz + "," \
                + mitglied.stadt + "," \
                + mitglied.land + "\n")

    return HttpResponse("OK")
