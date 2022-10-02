from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django import forms

from .models import Mitgliedschaftsantrag
from profil.models import Sichtbarkeit
from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp

from datetime import date
from random import choice

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

def neuerantrag(request):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = MitgliedschaftsantragForm(data=request.POST)
        if form.is_valid():
            ma = form.save(commit=False)
            ma.verifikationscode = ''.join(choice("ABCDEFGHKMNPQRSTUVWXYZ23456789") for _ in range(8))
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

    isadmin = request.user.is_superuser or request.user.groups.filter(name='vorstand').exists()

    return render(request,
                  'mitgliedschaftsantrag/antrag.html',
                  {'form': form,
                   'isadmin': isadmin,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
                  })


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def liste(request):
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

    return render(request, 'mitgliedschaftsantrag/liste.html',
                  {'verifikationen': verifikationen,
                   'antraege': antraege,
                  })


class MitgliedForm(forms.ModelForm):
    beitrag              = forms.BooleanField(required=False)
    beitrag_text         = forms.CharField(required=False)
    gutschrift           = forms.BooleanField(required=False)
    gutschrift_text      = forms.CharField(required=False)
    gutschrift_wert_cent = forms.IntegerField(required=False)
    mail                 = forms.BooleanField(required=False)

    sichtbarkeit_mailingliste   = forms.BooleanField(required=False)
    sichtbarkeit_adresse_verein = forms.BooleanField(required=False)
    sichtbarkeit_adresse_bwinf  = forms.BooleanField(required=False)
    sichtbarkeit_name_welt      = forms.BooleanField(required=False)

    class Meta:
        model = Mitglied
        exclude = ["austrittsdatum", "mitgliedsnummer", "anzahl_mahnungen"]


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def neuemitgliedschaft(request):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = MitgliedForm(data=request.POST)
        if form.is_valid():
            mitgliedsnummer = Mitglied.objects.order_by('-mitgliedsnummer')[0].mitgliedsnummer + 1
            m = form.save(commit=False)
            m.mitgliedsnummer = mitgliedsnummer
            m.save()

            setze_sichtbarkeiten(m,
                                 form.cleaned_data['sichtbarkeit_mailingliste'],
                                 form.cleaned_data['sichtbarkeit_adresse_verein'],
                                 form.cleaned_data['sichtbarkeit_adresse_bwinf'],
                                 form.cleaned_data['sichtbarkeit_name_welt'])

            if form.cleaned_data['mail']:
                if m.beitrittsdatum == None:
                    sende_email_mit_zahlungsinformationen(m)
                else:
                    benutzername = "m" + str(m.mitgliedsnummer)
                    passwort = ''.join(choice("ABCDEFGHKMNPQRSTUVWXYZabcdefghkmnpqrstuvwxyz23456789") for _ in range(16))
                    benutzer = User.objects.create_user(username=benutzername, email=m.email, password=passwort)
                    benutzermitglied = BenutzerMitglied(benutzer=benutzer, mitglied=m)
                    benutzermitglied.save()
                    sende_email_mit_zugangsdaten(m, passwort, benutzername)
            sende_email_an_vorstand(m, m.beitrittsdatum != None)

            if form.cleaned_data['beitrag']:
                try:
                    typ = MitgliedskontoBuchungstyp.objects.filter(typname="Mitgliedsbeitrag")[0]
                except:
                    typ = MitgliedskontoBuchungstyp.objects.create(typname="Mitgliedsbeitrag")
                MitgliedskontoBuchung.objects.create(mitglied=m, typ=typ, cent_wert=-m.beitrag_cent, kommentar=form.cleaned_data['beitrag_text'])

            if form.cleaned_data['gutschrift']:
                try:
                    typ = MitgliedskontoBuchungstyp.objects.filter(typname="Gutschrift")[0]
                except:
                    typ = MitgliedskontoBuchungstyp.objects.create(typname="Gutschrift")
                MitgliedskontoBuchung.objects.create(mitglied=m, typ=typ, cent_wert=form.cleaned_data['gutschrift_wert_cent'], kommentar=form.cleaned_data['gutschrift_text'])

            return redirect('mitgliedschaftsantrag:neuerantrag')
        else:
            errormessage = "Es sind Fehler aufgetreten. (S. o.)"
    else:
        form = MitgliedForm(initial={'beitrag': True,
                                     'beitrag_text': "Mitgliedsbeitrag " + str(date.today().year),
                                     'gutschrift_text': "Gutschrift Endrundenteilnahme (Endrunde " + str(date.today().year) + ")",
                                     'gutschrift_wert_cent': 2000,
                                     'mail': True})

    return render(request, 'mitgliedschaftsantrag/mitgliedschaft.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
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
            sende_email_an_vorstand(m, False)
            m.save()
            setze_sichtbarkeiten_antrag(m, ma)
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

class BeitragForm(forms.Form):
    beitrag              = forms.BooleanField(required=False)
    beitrag_text         = forms.CharField(required=False)
    gutschrift           = forms.BooleanField(required=False)
    gutschrift_text      = forms.CharField(required=False)
    gutschrift_wert_cent = forms.IntegerField(required=False)
    mail                 = forms.BooleanField(required=False)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def antrag(request, mitgliedsnummer):
    # 404 wenn Mitgliedschaft schon bestätigt
    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer, beitrittsdatum__exact = None)

    if request.method == 'POST':
        form = BeitragForm(request.POST)
        if form.is_valid():
            mitglied.beitrittsdatum = date.today()
            mitglied.save()

            if form.cleaned_data['mail']:
                benutzername = "m" + str(mitglied.mitgliedsnummer)
                passwort = ''.join(choice("ABCDEFGHKMNPQRSTUVWXYZabcdefghkmnpqrstuvwxyz23456789") for _ in range(16))
                benutzer = User.objects.create_user(username=benutzername, email=mitglied.email, password=passwort)
                benutzermitglied = BenutzerMitglied(benutzer=benutzer, mitglied=mitglied)
                benutzermitglied.save()
                sende_email_mit_zugangsdaten(mitglied, passwort, benutzername)

            sende_email_an_vorstand(mitglied, True)

            if form.cleaned_data['beitrag']:
                try:
                    typ = MitgliedskontoBuchungstyp.objects.filter(typname="Mitgliedsbeitrag")[0]
                except:
                    typ = MitgliedskontoBuchungstyp.objects.create(typname="Mitgliedsbeitrag")
                MitgliedskontoBuchung.objects.create(mitglied=mitglied, typ=typ, cent_wert=-mitglied.beitrag_cent, kommentar=form.cleaned_data['beitrag_text'])

            if form.cleaned_data['gutschrift']:
                try:
                    typ = MitgliedskontoBuchungstyp.objects.filter(typname="Gutschrift")[0]
                except:
                    typ = MitgliedskontoBuchungstyp.objects.create(typname="Gutschrift")
                MitgliedskontoBuchung.objects.create(mitglied=mitglied, typ=typ, cent_wert=form.cleaned_data['gutschrift_wert_cent'], kommentar=form.cleaned_data['gutschrift_text'])

            return redirect(reverse('mitgliedschaftsantrag:neuerantrag'))
        errormessage = "Something went wrong!"
        return render(request, 'mitgliedschaftsantrag/showantrag.html', {'antrag': antrag, 'form': form, 'errormessage': errormessage})
    else:
        antrag = {
            "id": mitglied.id,
            "mitgliedsnummer": mitglied.mitgliedsnummer,
            "name": mitglied.vorname + " " + mitglied.nachname,
            "datum": mitglied.antragsdatum,
            "beitrag_cent": mitglied.beitrag_cent,
            'vorname': mitglied.vorname,
            'nachname': mitglied.nachname,
            'anrede': mitglied.anrede,
            'geburtsdatum': mitglied.geburtsdatum,
            'strasse': mitglied.strasse,
            'adresszusatz': mitglied.adresszusatz,
            'plz': mitglied.plz,
            'stadt': mitglied.stadt,
            'land': mitglied.land,
            'telefon': mitglied.telefon,
            'email': mitglied.email,
            'beruf': mitglied.beruf,
            'studienort': mitglied.studienort,
            'studienfach': mitglied.studienfach,
        }
        form = BeitragForm(initial={'beitrag': True,
                                    'beitrag_text': "Mitgliedsbeitrag " + str(date.today().year),
                                    'gutschrift_text': "Gutschrift Beitritt am Jahresende",
                                    'gutschrift_wert_cent': 1000,
                                    'mail': True})

        return render(request,
                      'mitgliedschaftsantrag/showantrag.html',
                      {'antrag': antrag,
                       'form': form,
                       'errormessage': "",
                       })


def sende_email_mit_verifikationscode(mitgliedschaftsantrag):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + 'verifikation.txt', 'r', encoding='utf8') as templatefile:
            template = ""
            for line in templatefile.readlines():   # Remove first two character of every line if they are spaces
                template += line[2:] if line[:2] == "  " else line   # Allows for templates in dokuwiki syntax …
            data = {'name': mitgliedschaftsantrag.vorname + " " + mitgliedschaftsantrag.nachname,
                    'vorname': mitgliedschaftsantrag.vorname,
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
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + 'registrierung.txt', 'r', encoding='utf8') as templatefile:
            template = ""
            for line in templatefile.readlines():   # Remove first two character of every line if they are spaces
                template += line[2:] if line[:2] == "  " else line   # Allows for templates in dokuwiki syntax …
            data = {'name': mitglied.vorname + " " + mitglied.nachname,
                    'vorname': mitglied.vorname,
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

def sende_email_mit_zugangsdaten(mitglied, passwort, benutzername):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + 'aufnahmebestaetigung.txt', 'r', encoding='utf8') as templatefile:
            template = ""
            for line in templatefile.readlines():   # Remove first two character of every line if they are spaces
                template += line[2:] if line[:2] == "  " else line   # Allows for templates in dokuwiki syntax …
            data = {'name': mitglied.vorname + " " + mitglied.nachname,
                    'vorname': mitglied.vorname,
                    'nachname': mitglied.nachname,
                    'anrede': mitglied.anrede,
                    'mitgliedsnummer': mitglied.mitgliedsnummer,
                    'datum': str(date.today()),
                    'mitgliedsbeitrag': mitglied.beitrag_cent / 100.0,
                    'benutzername': benutzername,
                    'passwort': passwort,
                    'email': mitglied.email}
            betreff = "Zugangsdaten für Mitgliederbereich BwInf Alumni und Freunde e. V.".format(**data)
            text = template.format(**data)

            try:
                send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [mitglied.email])
                f.write("Date: " + str(date.today()) + "\n")
                f.write("To: " + mitglied.email + "\n")
                f.write("From: vorstand@alumni.bwinf.de\n")
                f.write("Subject: " + betreff + "\n\n")
                f.write(text + "\n\n")
            except:
                f.write("ERROR: Could not send mail to: " + mitglied.email + "(" + str(date.today()) + ": " + betreff + ") (" +  benutzername + ":" + passwort + ")\n\n")

def sende_email_an_vorstand(mitglied, aufgenommen):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        if aufgenommen:
            betrefftemplate = "Neuer Mitgliedschaftsantrag"
            template = """Ein neuer Mitgliedschaftsantrag ist eingegangen:

Name: {name}
Vorläufige Mitgliedsnummer: {mitgliedsnummer}
Mitgliedsbeitrag: {mitgliedsbeitrag} €

Sobald der Mitgliedsbeitrag eingegangen ist, kann der Mitgliedschafts-
antrag unter https://alumni.bwinf.de/mitgliedschaftsantrag/liste
bestätigt werden."""
        else:
            betrefftemplate = "Neues Mitglied aufgenommen! 🥳"
            template = """Ein neues Mitglied wurde in den Verein aufgenommen:

Name: {name}
Mitgliedsnummer: {mitgliedsnummer}
Mitgliedsbeitrag: {mitgliedsbeitrag} €

🥳🥳🥳"""

        data = {'name': mitglied.vorname + " " + mitglied.nachname,
                'vorname': mitglied.vorname,
                'nachname': mitglied.nachname,
                'anrede': mitglied.anrede,
                'mitgliedsnummer': mitglied.mitgliedsnummer,
                'datum': str(date.today()),
                'mitgliedsbeitrag': mitglied.beitrag_cent / 100.0,
                'email': mitglied.email}

        betreff = betrefftemplate.format(**data)
        text = template.format(**data)

        try:
            send_mail(betreff, text, 'vorstand@alumni.bwinf.de', ['vorstand@alumni.bwinf.de'])
            f.write("Date: " + str(date.today()) + "\n")
            f.write("To: vorstand@alumni.bwinf.de\n")
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
    m.strasse      = ma.strasse
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
                 ("alumni", "adresse"),
                 ("alumni", "karte")]
profil_bwinf = [("bwinf", "vorname"),
                ("bwinf", "nachname"),
                ("bwinf", "email"),
                ("bwinf", "adresse")]
profil_welt = [("welt", "vorname"),
               ("welt", "nachname")]

def setze_sichtbarkeiten(m, mailingliste, adresse_verein, adresse_bwinf, name_welt):
    profil = profil_default.copy()
    if mailingliste:
        profil += profil_mailingliste
    if adresse_verein:
        profil += profil_verein
    if adresse_bwinf:
        profil += profil_bwinf
    if name_welt:
        profil += profil_welt

    for (bereich, sache) in profil:
        neu = Sichtbarkeit.objects.create(mitglied=m,
                                          bereich=bereich,
                                          sache=sache)

def setze_sichtbarkeiten_antrag(m, ma):
    setze_sichtbarkeiten(m,
                         ma.mailingliste,
                         ma.adresse_verein,
                         ma.adresse_bwinf,
                         ma.name_welt)
