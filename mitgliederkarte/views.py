from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test
from mitglieder.models import Mitglied

import math
import datetime

# Create your views here.

plzs = None

def load_plz():
    global plzs
    
    if plzs is not None:
        return
    
    plzs = {}
    
    try:
        with open("mitgliederkarte/data/PLZ.tab", "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                entries = line.split("\t")
                plz = entries[1]
                lon = float(entries[2])
                lat = float(entries[3])
                plzs[plz] = (lon, lat)
    except:
        plzs = None
    


def plz_to_coord(plz):
    global plzs
    
    load_plz()
    
    if plzs is None:
        return
    
    if not plz in plzs:
        return None
    else:
        return plzs[plz]
    

#@login_required
#@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def index(request):
    is_authenticated = request.user.is_authenticated
    
    try:
        ownmitglied = request.user.benutzermitglied.mitglied
    except:
        ownmitglied = None
    
    
    bereich = "welt" if not is_authenticated else "alumni"
    
    plzmitglieder = {}
    
    mitgliedercoords = []
    
    wohnort_mitglieder = Mitglied.objects.filter(sichtbarkeit__bereich=bereich, sichtbarkeit__sache='wohnort')
    adresse_mitglieder = Mitglied.objects.filter(sichtbarkeit__bereich=bereich, sichtbarkeit__sache='adresse')
    
    today = datetime.datetime.today()
    
    all_mitglieder = wohnort_mitglieder.union(adresse_mitglieder).filter(beitrittsdatum__lte=today).exclude(austrittsdatum__lte=today)
    
    for mitglied in all_mitglieder:
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
        
            mtext = [m.vorname, m.nachname, m.plz, m.stadt, "/profil/"+str(m.mitgliedsnummer)]
            
            do_highlight = (ownmitglied is not None and m.mitgliedsnummer == ownmitglied.mitgliedsnummer)
            
            mitgliedercoords.append( [do_highlight, mlon, mlat, mtext]  )
        
    
    
    return render(request, 'mitgliederkarte/karte.html', {'coords': mitgliedercoords})

