from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
import re

from .models import Sichtbarkeit
from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied
from django.contrib.auth.models import User

from django import forms
from django.forms import formset_factory

from datetime import date

sichtbarkeiten   = [("alumni", "vorname"),
                    ("alumni", "nachname"),
                    ("alumni", "studienort"),
                    ("alumni", "studienfach"),
                    ("alumni", "beruf"),
                    ("alumni", "email"),
                    ("alumni", "telefon"),
                    ("alumni", "adresse"),
                    ("alumni", "mailingliste"),
                    ("bwinf", "vorname"),
                    ("bwinf", "nachname"),
                    ("bwinf", "email"),
                    ("bwinf", "telefon"),
                    ("bwinf", "adresse"),
                    ("welt", "vorname"),
                    ("welt", "nachname"),
                    ("welt", "studienort"),
                    ("welt", "studienfach"),
                    ("welt", "beruf"),
                    ("welt", "email"),
                    ("welt", "telefon"),
                    ("welt", "adresse"),
                    ("alumni", "karte"),
                    ("welt", "karte"),
                    ]



class MitgliedForm(forms.ModelForm):
    class Meta:
        model = Mitglied
        fields = ['anrede', 'strasse', 'adresszusatz', 'plz', 'stadt', 'land', 'telefon', 'beruf', 'studienort', 'studienfach']

@login_required
def index(request):
    benutzer = request.user
    try:
        mitglied = benutzer.benutzermitglied.mitglied
    except:
        raise Http404("Keine Benutzerinformationen vorhanden.")

    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = MitgliedForm(instance=mitglied, data=request.POST)
        if form.is_valid():
            form.save()
            successmessage = "Profil aktualisiert. Bitte überprüfe, ob deine Daten in der Mitgliederliste richtig angezeigt werden."
        else:
            errormessage = "Es sind Fehler aufgetreten."
    else:
        form = MitgliedForm(instance=mitglied)


    sichtbar = [Sichtbarkeit.objects.filter(mitglied=mitglied)
                                    .filter(bereich=sb[0])
                                    .filter(sache=sb[1])
                                    .exists() for sb in sichtbarkeiten]

    return render(request, 'profil/profil.html', {'form': form,
                                                  'mitglied': mitglied,
                                                  'benutzername': benutzer.username,
                                                  'benutzeremail': benutzer.email,
                                                  'errormessage': errormessage,
                                                  'successmessage': successmessage,
                                                  'sichtbar': sichtbar})


def showuser(request, mitgliedid):
    is_authenticated = request.user.is_authenticated
    scope = "alumni" if is_authenticated else "welt"

    mitglied = get_object_or_404(Mitglied, id__exact = mitgliedid)
    info = {}
    keine_info = True
    for sache in ["vorname", "nachname", "studienort", "studienfach", "beruf", "email", "telefon", "adresse", "karte"]:
        if sichtbar(mitglied, scope, sache):
            keine_info = False
            info[sache] = True
    if keine_info:
        raise Http404("Keine Benutzerinformationen vorhanden.")

    info['land_fett'] = mitglied.land.upper()
    info['email_sanitised'] = mitglied.email.replace("@", " [ bei ] ")
    info["mitglied"] = mitglied
    info["initiale"] = mitglied.vorname[0].upper()

    return render(request, 'profil/anzeige.html', {'info': info})

def sichtbar(mitglied, bereich, sache):
    return mitglied.sichtbarkeit_set.filter(bereich=bereich).filter(sache=sache).exists()

def showallusers(request):
    is_authenticated = request.user.is_authenticated
    scope = "alumni" if is_authenticated else "welt"

    today = date.today()
    mitglieder = Mitglied.objects.filter(beitrittsdatum__lte = today).exclude(austrittsdatum__lte = today).prefetch_related('sichtbarkeit_set').order_by('vorname')

    infos = []
    for mitglied in mitglieder:
        info = {}
        keine_info = True
        for sache in ["vorname", "nachname", "studienort", "studienfach", "beruf", "email", "telefon", "adresse", "karte"]:
            if sichtbar(mitglied, scope, sache):
                keine_info = False
                info[sache] = True
        if not keine_info:
            info["mitglied"] = mitglied
            info["initiale"] = mitglied.vorname[0].upper()
            infos.append(info)
    return render(request, 'profil/mitgliederliste.html', {'infos': infos})

class SichtbarkeitForm(forms.Form):
    sichtbarkeit = forms.BooleanField(required=False)

@login_required
def sichtbarkeit(request):
    benutzer = request.user
    try:
        mitglied = benutzer.benutzermitglied.mitglied
    except:
        raise Http404("Keine Benutzerinformationen vorhanden.")

    errormessage = ""
    successmessage = ""

    SichtbarkeitFormSet = formset_factory(SichtbarkeitForm)

    if request.method == 'POST':
        form = SichtbarkeitFormSet(data=request.POST)
        if form.is_valid():
            i = 0
            for sichtbarkeit in sichtbarkeiten:
                if Sichtbarkeit.objects.filter(mitglied=mitglied).filter(bereich=sichtbarkeit[0]).filter(sache=sichtbarkeit[1]).exists():
                    if i >= 6 and not form[i].cleaned_data["sichtbarkeit"]:
                        Sichtbarkeit.objects.filter(mitglied=mitglied).filter(bereich=sichtbarkeit[0]).filter(sache=sichtbarkeit[1]).delete()
                else:
                    if i < 6 or form[i].cleaned_data["sichtbarkeit"]:
                        neu = Sichtbarkeit.objects.create(mitglied=mitglied,
                                                          bereich=sichtbarkeit[0],
                                                          sache=sichtbarkeit[1])

                i += 1

            successmessage = "Einstellungen aktualisiert. Bitte überprüfe, ob deine Daten in der Mitgliederliste richtig angezeigt werden."
        else:
            errormessage = "Es sind Fehler aufgetreten."
    else:
        initial = [] # array of dicts with boolean value for the checkboxes
        for sichtbarkeit in sichtbarkeiten:
            initial.append({'sichtbarkeit': Sichtbarkeit.objects.filter(mitglied=mitglied)
                                                        .filter(bereich=sichtbarkeit[0])
                                                        .filter(sache=sichtbarkeit[1])
                                                        .exists()})
        form = SichtbarkeitFormSet(initial=initial)

    return render(request, 'profil/sichtbarkeit.html', {'form': form, 'mitglied': mitglied, 'errormessage': errormessage, 'successmessage': successmessage})
