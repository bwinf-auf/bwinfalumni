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
            successmessage = "Profil aktualisiert."
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
                                                  'errormessage': errormessage,
                                                  'successmessage': successmessage, 
                                                  'sichtbar': sichtbar})  


@login_required
def showuser(request, userid):
    benutzer = get_object_or_404(User, id__exact = userid)
    try:
        mitglied = benutzer.benutzermitglied.mitglied
    except:
        raise Http404("Keine Benutzerinformationen vorhanden.")
    
    return render(request, 'benutzer/anzeige.html', {'benutzer': benutzer,
                                                        'mitglied': mitglied,
                                                        })

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
    
    SichtbarkeitFormSet = formset_factory(SichtbarkeitForm, extra=15)
    
    if request.method == 'POST':
        form = SichtbarkeitFormSet(data=request.POST)
        if form.is_valid():
            i = 0
            for sichtbarkeit in sichtbarkeiten:
                if i >= 6 and Sichtbarkeit.objects.filter(mitglied=mitglied).filter(bereich=sichtbarkeit[0]).filter(sache=sichtbarkeit[1]).exists():
                    if not form[i].cleaned_data["sichtbarkeit"]:
                        Sichtbarkeit.objects.filter(mitglied=mitglied).filter(bereich=sichtbarkeit[0]).filter(sache=sichtbarkeit[1]).delete()
                else:
                    if i < 6 or form[i].cleaned_data["sichtbarkeit"]:
                        neu = Sichtbarkeit.objects.create(mitglied=mitglied,
                                                          bereich=sichtbarkeit[0],
                                                          sache=sichtbarkeit[1])
                
                i += 1
            
            successmessage = "Einstellungen aktualisiert."
        else:
            errormessage = "Es sind Fehler aufgetreten."
    else:
        initial = []
        for sichtbarkeit in sichtbarkeiten:
            initial.append({'sichtbarkeit': Sichtbarkeit.objects.filter(mitglied=mitglied)
                                                        .filter(bereich=sichtbarkeit[0])
                                                        .filter(sache=sichtbarkeit[1])
                                                        .exists()})
        form = SichtbarkeitFormSet(initial=initial)
    
    return render(request, 'profil/sichtbarkeit.html', {'form': form, 'mitglied': mitglied, 'errormessage': errormessage, 'successmessage': successmessage})  

