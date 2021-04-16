from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from django import forms

from django.core.mail import send_mail

from .models import Mitgliedschaftsantrag
from mitglieder.models import Mitglied
from profil.models import Sichtbarkeit

from datetime import date
import random
import string

class MitgliedschaftsantragForm(forms.ModelForm):
    class Meta:
        model = Mitgliedschaftsantrag
        fields = ['vorname', 'nachname', 'anrede', 'geburtsdatum', 'email', 'mitgliedschaft', 'mitgliedsbeitrag', 'strasse', 'adresszusatz', 'plz', 'stadt', 'land', 'telefon', 'beruf', 'studienort', 'studienfach', 'mailingliste', 'adresse_verein', 'adresse_bwinf', 'name_welt']
        widgets = { 'mitgliedschaft': forms.RadioSelect }
        labels = {
            'vorname': "Vorname*",
            'nachname': "Nachname*",
            'geburtsdatum': "Geburtsdatum*",
            'email': "E-Mailadresse*",
            'mitgliedschaft': "Vereinsmitgliedschaft*",
            'strasse': "Straße, Hausnummer*",
            'plz': "Postleitzahl*",
            'stadt': "Ort*",

            'beruf': "Beschäftigung" }

def antrag(request):
    antraege = None
    verifikationen = None

    benutzer = request.user
    if benutzer.is_superuser or benutzer.groups.filter(name='vorstand').exists():
        verifikationen = []
        for ma in Mitgliedschaftsantrag.objects.all():
            verifikationen.append({
                "id": ma.id,
                "name": ma.vorname + " " + ma.nachname,
                "datum": ma.antragsdatum,
                "code": ma.verifikationscode,
                "email": ma.email,
            })
        antraege = []
        for m in Mitglied.objects.filter(beitrittsdatum__isnull=True):
            antraege.append({
                "id": m.id,
                "mitgliedsnummer": m.mitgliedsnummer,
                "name": m.vorname + " " + m.nachname,
                "datum": m.antragsdatum,
            })



    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = MitgliedschaftsantragForm(data=request.POST)
        if form.is_valid():
            ma = form.save(commit=False)
            ma.verifikationscode = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
            if ma.mitgliedschaft == 'O' or ma.mitgliedsbeitrag >= 50:
                if ma.mitgliedschaft == 'O':
                    ma.mitgliedsbeitrag = 10
                sende_email_mit_verifikationscode(ma)
                ma.save()
                return redirect('mitgliedschaftsantrag:verifikation')
            else:
                errormessage = "Für Fördermitglieder soll der Mitgliedsbeitrag 50 € nicht unterschreiten."
        else:
            errormessage = "Es sind Fehler aufgetreten. (S. o.)"
    else:
        form = MitgliedschaftsantragForm()

    return render(request, 'mitgliedschaftsantrag/antrag.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
                   'verifikationen': verifikationen,
                   'antraege': antraege,
                  })

class VerifikationForm(forms.Form):
    code = forms.CharField(label='Verifikationscode', max_length=250)

def verifikation(request, code=None):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = VerifikationForm(data=request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
        else:
            errormessage = "Es sind Fehler aufgetreten."
    else:
        form = VerifikationForm()

    if code != None:
        try:
            ma = Mitgliedschaftsantrag.objects.get(verifikationscode = code)
            m = vorlaeufiges_mitglied(ma)
            sende_email_mit_zahlungsinformationen(m)
            m.save()
            setze_sichtbarkeiten(ma, m)
            ma.delete()
            return redirect(reverse('mitgliedschaftsantrag:zahlungsinformationen', kwargs={'mitgliedsnummer':m.mitgliedsnummer}))
        except ObjectDoesNotExist: # Kein Mitgliedschaftsantrag mit diesem Code vorhanden
            errormessage = "Dieser Code ist nicht gültig. Möglicherweise wurde die E-Mailadresse bereits erfolgreich verifiziert."

    return render(request, 'mitgliedschaftsantrag/verifikation.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
                  })

def zahlungsinformationen(request, mitgliedsnummer):
    # 404 wenn Mitgliedschaft schon bestätigt, damit keine Beitragsinformationen extrahiert werden können.
    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer, beitrittsdatum__exact = None)


    return render(request, 'mitgliedschaftsantrag/zahlungsinformationen.html',
                  {'mitgliedsnummer': mitglied.mitgliedsnummer,
                   'mitgliedsbeitrag': mitglied.beitrag_cent / 100.0,
                  })


def sende_email_mit_verifikationscode(mitgliedschaftsantrag):
    with open('listen/maillog', 'a', encoding='utf8') as f:
        with open ("mitgliedschaftsantrag/verifikation.txt", "r", encoding='utf8') as templatefile:
            template = templatefile.read()
            data = {'vorname': mitgliedschaftsantrag.vorname,
                    'nachname': mitgliedschaftsantrag.nachname,
                    'anrede': mitgliedschaftsantrag.anrede,
                    'datum': str(date.today()),
                    'mitgliedsbeitrag': mitgliedschaftsantrag.mitgliedsbeitrag,
                    'email': mitgliedschaftsantrag.email,
                    'code': mitgliedschaftsantrag.verifikationscode}
            betreff = "E-Mailverifikation BwInf Alumni und Freunde e. V.".format(**data)
            text = template.format(**data)

            try:
                send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [mitgliedschaftsantrag.email])
                f.write("Date: " + str(date.today()) + "\n")
                f.write("To: " + mitgliedschaftsantrag.email + "\n")
                f.write("From: vorstand@alumni.bwinf.de\n")
                f.write("Subject: " + betreff + "\n\n")
                f.write(text + "\n\n")
            except:
                f.write("ERROR: Could not send mail to: " + mitgliedschaftsantrag.email + "(" + str(date.today()) + ": " + betreff + ") (code: " +  mitgliedschaftsantrag.verifikationscode + ")\n\n")

def sende_email_mit_zahlungsinformationen(mitglied):
    with open('listen/maillog', 'a', encoding='utf8') as f:
        with open ("mitgliedschaftsantrag/registrierung.txt", "r", encoding='utf8') as templatefile:
            template = templatefile.read()
            data = {'vorname': mitglied.vorname,
                    'nachname': mitglied.nachname,
                    'anrede': mitglied.anrede,
                    'mitgliedsnummer': mitglied.mitgliedsnummer,
                    'datum': str(date.today()),
                    'mitgliedsbeitrag': mitglied.beitrag_cent / 100.0,
                    'email': mitglied.email}
            betreff = "Mitgliedschaftsantrag BwInf Alumni und Freunde e. V.".format(**data)
            text = template.format(**data)

            try:
                send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [mitglied.email])
                f.write("Date: " + str(date.today()) + "\n")
                f.write("To: " + mitglied.email + "\n")
                f.write("From: vorstand@alumni.bwinf.de\n")
                f.write("Subject: " + betreff + "\n\n")
                f.write(text + "\n\n")
            except:
                f.write("ERROR: Could not send mail to: " + mitglied.email + "(" + str(date.today()) + ": " + betreff + ")\n\n")


def vorlaeufiges_mitglied(ma):
    mitgliedsnummer = Mitglied.objects.order_by('-mitgliedsnummer')[0].mitgliedsnummer + 1

    m = Mitglied()
    m.mitgliedsnummer = mitgliedsnummer
    m.beitrittsdatum  = None
    m.beitrag_cent = ma.mitgliedsbeitrag * 100
    m.vorname      = ma.vorname
    m.nachname     = ma.nachname
    m.anrede       = ma.anrede
    m.geburtsdatum = ma.geburtsdatum
    m.adresse      = ma.strasse
    m.adresszusatz = ma.adresszusatz
    m.plz          = ma.plz
    m.stadt        = ma.stadt
    m.land         = ma.land if ma.land != "" else "Deutschland"
    m.telefon      = ma.telefon
    m.email        = ma.email
    m.beruf        = ma.beruf
    m.studienort   = ma.studienort
    m.studienfach  = ma.studienfach

    return m

profil_default = [("alumni", "vorname"),
                  ("alumni", "nachname"),
                  ("alumni", "studienort"),
                  ("alumni", "studienfach"),
                  ("alumni", "beruf"),
                  ("alumni", "email")]
profil_mailingliste = [("alumni", "mailingliste")]
profil_verein = [("alumni", "telefon"),
                 ("alumni", "adresse")]
profil_bwinf = [("bwinf", "vorname"),
                ("bwinf", "nachname"),
                ("bwinf", "email"),
                ("bwinf", "adresse")]
profil_welt = [("welt", "vorname"),
               ("welt", "nachname")]

def setze_sichtbarkeiten(ma, m):
    profil = profil_default.copy()
    if ma.mailingliste:
        profil += profil_mailingliste
    if ma.adresse_verein:
        profil += profil_verein
    if ma.adresse_bwinf:
        profil += profil_bwinf
    if ma.name_welt:
        profil += profil_welt

    for (bereich, sache) in profil:
        neu = Sichtbarkeit.objects.create(mitglied=m,
                                          bereich=bereich,
                                          sache=sache)
