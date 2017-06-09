from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
import re

from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied
from django.contrib.auth.models import User

from django import forms

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
    
    return render(request, 'profil/profil.html', {'form': form, 'mitglied': mitglied, 'errormessage': errormessage, 'successmessage': successmessage})  



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
