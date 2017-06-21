from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.models import User
from .models import Mitglied
from benutzer.models import BenutzerMitglied

from datetime import date

from django import forms



@login_required
@user_passes_test(lambda u: u.is_superuser)
def mitglieder(request):
    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')
    return render(request, 'mitglieder/mitgliederliste.html', {'mitglieder': all_mitglieder})  

class TestFailed(Exception):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message


@login_required
def mitglied(request, mitgliedsnummer):
    benutzer = request.user
    try:
        mitglied = benutzer.benutzermitglied.mitglied
    except:
        if not benutzer.is_superuser:
            raise Http404("Keine Benutzerinformationen vorhanden.")

    if mitglied.mitgliedsnummer != int(mitgliedsnummer) and not benutzer.is_superuser:
        raise TestFailed(str(mitglied.mitgliedsnummer))
    
    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)
    all_transactions = []
    value = 0
    for buchung in mitglied.mitgliedskontobuchung_set.all(): 
        value += buchung.centWert
        all_transactions.append({'amount': buchung.centWert / 100.0,
                                 'comment': buchung.kommentar,
                                 'value': value / 100.0})    
    return render(request, 'mitglieder/mitglied.html', {'mitglied': mitglied, 'transactions': all_transactions, 'before': 0.0, 'after': value/100.0})



class MitgliedForm(forms.ModelForm):
    class Meta:
        model = Mitglied
        fields = ['mitgliedsnummer', 'vorname', 'nachname', 'beitrittsdatum']

class AddUserForm(forms.Form):
    adduserp = forms.BooleanField(label='Benutzer-Account anlegen', required=False)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

@login_required
@user_passes_test(lambda u: u.is_superuser)
def addmitglied(request):
    if request.method == 'POST':
        mform = MitgliedForm(request.POST)
        pform = AddUserForm(request.POST)
        bform = UserForm(request.POST)
        
        errormessage = ""
        successmessage = ""
        
        if not mform.is_valid():
            errormessage = "Die eingegebenen Daten sind ungültig. " + mform.errors.as_json(escape_html=True)
        elif not pform.is_valid():
            errormessage = "Die eingegebenen Daten sind ungültig. " + pform.errors.as_json(escape_html=True)
        else:
            mform.save()
            if pform.cleaned_data['adduserp']:
                if not bform.is_valid():
                    errormessage = "Die eingegebenen Daten sind ungültig. " + bform.errors.as_json(escape_html=True)
                else: 
                    bform.instance.is_staff = True
                    bform.save()
                    benutzerinfo = BenutzerInformation()
                    benutzerinfo.user = bform.instance
                    benutzerinfo.mitglied = mform.instance
                    benutzerinfo.save()
                    
        if errormessage == "":
            successmessage = "Mitglied wurde erfolgreich hinzugefügt."
        return render(request, 'mitglieder/adddone.html', {'errormessage': errormessage,
                                                           'successmessage': successmessage,}) 
    
    else: # GET or something
        hochste_mitgliedernummer = Mitglied.objects.order_by('mitgliedsnummer').reverse()[0].mitgliedsnummer;
        return render(request, 'mitglieder/addform.html', {'mform': MitgliedForm({'mitgliedsnummer': hochste_mitgliedernummer + 1, 
                                                                                  'beitrittsdatum': date.today()}),
                                                           'pform': AddUserForm(),
                                                           'bform': UserForm()}) 
  
