from django.shortcuts import render
from django.conf import settings

from django.contrib.auth.decorators import login_required, user_passes_test
from mitglieder.models import Mitglied

import math
import datetime

plzs = {}

with open(settings.BWINFALUMNI_BASE_DIR + 'mitgliederkarte/data/PLZ.tab', 'r', encoding='utf8') as f:
    for line in f:
        if line.startswith("#"):
            continue
        entries = line.split("\t")
        plz = entries[1]
        lon = float(entries[2])
        lat = float(entries[3])
        plzs[plz] = (lon, lat)

def plz_to_coord(plz):
    global plzs

    if not plz in plzs:
        return None
    else:
        return plzs[plz]


def index(request):
    is_authenticated = request.user.is_authenticated

    try:
        ownmitglied = request.user.benutzermitglied.mitglied
    except:
        ownmitglied = None

    bereich = "welt" if not is_authenticated else "alumni"

    today = datetime.datetime.today()
    karte_mitglieder = Mitglied.objects.filter(sichtbarkeit__bereich=bereich, sichtbarkeit__sache='karte')
    karte_mitglieder = karte_mitglieder.filter(beitrittsdatum__lte=today).exclude(austrittsdatum__lte=today)

    plzmitglieder = {}
    mitgliedercoords = []

    for mitglied in karte_mitglieder:
        plz = mitglied.plz
        land = mitglied.land

        if land.lower() not in ["de", "deutschland"]:
            continue

        if not plz in plzmitglieder:
            plzmitglieder[plz] = [mitglied]
        else:
            plzmitglieder[plz].append(mitglied)

    for plz in plzmitglieder:
        coords = plz_to_coord(plz)
        if coords is None:
            continue

        num = len(plzmitglieder[plz])
        delta = math.sqrt(num-1)*0.01

        for i in range(len(plzmitglieder[plz])):
            m = plzmitglieder[plz][i]

            mlon = coords[0] + delta*math.cos(2.*math.pi * i/num)
            mlat = coords[1] + delta*math.sin(2.*math.pi * i/num)

            mtext = [m.vorname, m.nachname, m.plz, m.stadt, "/profil/"+str(m.id)]

            do_highlight = (ownmitglied is not None and m.mitgliedsnummer == ownmitglied.mitgliedsnummer)

            mitgliedercoords.append( [do_highlight, mlon, mlat, mtext]  )

    return render(request, 'mitgliederkarte/karte.html', {'coords': mitgliedercoords})
