from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.models import User
from .models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp
from benutzer.models import BenutzerMitglied

from django.core.mail.backends.smtp import EmailBackend

from datetime import date

from django import forms
from django.shortcuts import redirect
from django.forms import ModelForm

from django.core.mail import send_mail

from bwinfalumni.settings import DEBUG

from django.core.urlresolvers import reverse
# in neuern django versionen from django.urls import reverse


@login_required
def index(request):
    benutzer = request.user
    
    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        return redirect(reverse('mitglieder:detail', kwargs={'mitgliedsnummer':mitglied.mitgliedsnummer}))
    
    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')
    return render(request, 'mitglieder/mitgliederliste.html', {'mitglieder': all_mitglieder})  



class MitgliedskontoBuchungForm(ModelForm):
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['typ', 'cent_wert', 'kommentar', 'buchungsdatum']


@login_required
def detail(request, mitgliedsnummer):
    benutzer = request.user
    
    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        if mitglied.mitgliedsnummer != int(mitgliedsnummer):
            raise Http404("Kein Zugriff (" + str(mitglied.mitgliedsnummer) + ")")
    
    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)
    
    if request.method == 'POST':
        mkbuchung = MitgliedskontoBuchungForm(request.POST)
        if mkbuchung.is_valid():
            buchung = mkbuchung.save(commit=False)
            buchung.mitglied = mitglied
            buchung.save()
            mkbuchung = MitgliedskontoBuchungForm()
    else:
        mkbuchung = MitgliedskontoBuchungForm()
    
    all_transactions = []
    value = 0
    for buchung in mitglied.mitgliedskontobuchung_set.all().order_by('buchungsdatum'): 
        value += buchung.cent_wert
        all_transactions.append({'amount': buchung.cent_wert / 100.0,
                                 'comment': buchung.kommentar,
                                 'value': value / 100.0, 
                                 'date': buchung.buchungsdatum,
                                 'type': buchung.typ.typname,
                                 })    
    return render(request, 'mitglieder/mitglied.html', {'mitglied': mitglied, 'transactions': all_transactions, 'before': 0.0, 'after': value/100.0, 'form': mkbuchung})



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
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def addmitglied(request):
    if not DEBUG:
        raise Http404("Mitglieder-Anlegen zur Zeit noch nicht verfügbar.")
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

class BeitraegeForm(ModelForm):
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['cent_wert', 'kommentar', 'buchungsdatum']

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def beitraegeeinziehen(request):
    if request.method == 'POST':
        bform = BeitraegeForm(request.POST)
        
        errormessage = ""
        successmessage = ""
        
        if not bform.is_valid():
            errormessage = "Die eingegebenen Daten sind ungültig. " + mform.errors.as_json(escape_html=True)
        else:
            typ = MitgliedskontoBuchungstyp(typname = bform.cleaned_data['kommentar'])
            typ.save()
            today = date.today()
            mitglieder = Mitglied.objects.filter(beitrittsdatum__lte = today)
            numBeitraege = 0
            for mitglied in mitglieder:
                buchung = MitgliedskontoBuchung(mitglied = mitglied,
                                                typ = typ,
                                                cent_wert = bform.cleaned_data['cent_wert'], 
                                                kommentar = bform.cleaned_data['kommentar'],
                                                buchungsdatum = bform.cleaned_data['buchungsdatum'])
                buchung.save()
                numBeitraege += 1
        
        if errormessage == "":
            successmessage = "Beitraeg von " + str(numBeitraege) + " Mitgliedern wurden erfolgreich abgebucht."
        
        return render(request, 'mitglieder/adddone.html', {'errormessage': errormessage,
                                                           'successmessage': successmessage,})
    else:
        return render(request, 'mitglieder/beitraege.html', {'bform': BeitraegeForm({'cent_wert': -1000,
                                                                                   'kommentar': "Mitgliedsbeitrag " + str(date.today().year), 
                                                                                   'buchungsdatum': date.today()})})


class EmailForm(forms.Form):
    betreff = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())    
def zahlungsaufforderungen(request, template, schulden):
    if request.method == 'POST':
        cform = EmailForm(request.POST)
        
        errormessage = ""
        successmessage = ""
        
        if not cform.is_valid():
            errormessage = "Es müssen Text und Titel angegeben werden. " + mform.errors.as_json(escape_html=True)
        else:
            today = date.today()
            mitglieder = Mitglied.objects.filter(beitrittsdatum__lte = today)
            numEmails = 0
            failEmails = 0
            with open('maillog', 'w') as f:
                for mitglied in mitglieder:
                    kontostand = 0
                    buchungen = mitglied.mitgliedskontobuchung_set.all()
                    for buchung in buchungen:
                        kontostand += buchung.cent_wert
                    if kontostand < 0 or not schulden:
                        data = {'vorname': mitglied.vorname,
                                'nachname': mitglied.nachname,
                                'anrede': mitglied.anrede,
                                'mitgliedsnummer': mitglied.mitgliedsnummer,
                                'datum': str(date.today()),
                                'kontostand': kontostand / 100.0,
                                'schulden': -kontostand / 100.0,
                                'email': mitglied.email}
                        betreff = cform.cleaned_data['betreff'].format(**data)
                        text = cform.cleaned_data['text'].format(**data)
                        
                        try:
                            send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [mitglied.email])
                            f.write("Date: " + str(date.today()) + "\n")
                            f.write("To: " + mitglied.email + "\n")
                            f.write("From: vorstand@alumni.bwinf.de\n")
                            f.write("Subject: " + betreff + "\n\n")
                            f.write(text + "\n\n")
                            numEmails += 1
                        except:
                            f.write("ERROR: Could not send mail to: " + mitglied.email + "(" + str(date.today()) + ": " + betreff + ")\n\n")
                            failEmails += 1;
        
        if errormessage == "":
            successmessage = "E-Mail an " + str(numEmails) + " Mitglieder wurde erfolgreich versandt. " + str(failEmails) + " E-Mails konnten nicht versandt werden."
        
        return render(request, 'mitglieder/adddone.html', {'errormessage': errormessage,
                                                           'successmessage': successmessage,})
    else: 
        text = ""
        with open ("mitglieder/" + template + ".txt", "r") as templatefile:
            text = templatefile.read()
        return render(request, 'mitglieder/email.html', {'cform': EmailForm({'betreff': "Mitgliedsbeitrag BwInf Alumni und Freunde e. V.",
                                                                            'text': text}), 'schulden': schulden})
