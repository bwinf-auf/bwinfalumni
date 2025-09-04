from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.template import loader
from django.forms import ModelForm
from django.http import HttpResponse, Http404
from django.conf import settings
from django.urls import reverse
from django import forms

from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp
from verein.models import Freistellungsbescheid

from datetime import date
import os.path
import json

@login_required
def index(request):
    benutzer = request.user

    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        return redirect(reverse('mitgliedskonto:detail', kwargs={'mitgliedsnummer':mitglied.mitgliedsnummer}))

    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')
    return render(request, 'mitgliedskonto/mitgliederliste.html', {'mitglieder': all_mitglieder})



class MitgliedskontoBuchungForm(ModelForm):
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['typ', 'cent_wert', 'kommentar', 'buchungsdatum', 'wirksam']


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
        if buchung.wirksam:
            value += buchung.cent_wert
        all_transactions.append({'amount': buchung.cent_wert / 100.0,
                                 'comment': buchung.kommentar,
                                 'value': value / 100.0,
                                 'date': buchung.buchungsdatum,
                                 'type': buchung.typ.typname,
                                 'large': buchung.cent_wert >= 5000,
                                 'id': buchung.pk,
                                 'beleg_status': buchung.beleg_status,
                                 })
    return render(request, 'mitgliedskonto/mitglied.html', {'mitglied': mitglied, 'transactions': all_transactions, 'before': 0.0, 'after': value/100.0, 'form': mkbuchung})


@login_required
def bescheinigung(request, mitgliedsnummer, mitgliedskontobuchungsnummer):
    benutzer = request.user

    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        if mitglied.mitgliedsnummer != int(mitgliedsnummer):
            raise Http404("Kein Zugriff (" + str(mitglied.mitgliedsnummer) + ")")

    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)
    mitgliedskontobuchung = get_object_or_404(MitgliedskontoBuchung, pk = mitgliedskontobuchungsnummer)
    if mitglied != mitgliedskontobuchung.mitglied:
        raise Http404("Buchung nicht gefunden.")

    if mitgliedskontobuchung.beleg_status == "verifiziert" or (mitgliedskontobuchung.beleg_status != "" and (benutzer.is_superuser or benutzer.groups.filter(name='vorstand').exists())):
        if not os.path.isfile(settings.BWINFALUMNI_INVOICE_DIR + str(mitglied.mitgliedsnummer) + '_' + str(mitgliedskontobuchung.pk) + '.pdf'):
            raise Http404("Datei nicht vorhanden.")

        with open(settings.BWINFALUMNI_INVOICE_DIR + str(mitglied.mitgliedsnummer) + '_' + str(mitgliedskontobuchung.pk) + '.pdf', 'rb') as f:
            return HttpResponse(
                f,
                content_type='application/pdf',
                headers={
                    'Content-Disposition': f"attachment; filename={mitgliedskontobuchung.pk}.pdf",
                    'Cache-Control': 'no-cache'  # files are dynamic, prevent caching
                }
            )

    if mitgliedskontobuchung.beleg_status != "":
        raise Http404("Buchung nicht gefunden.")

    mitgliedskontobuchung.beleg_status = "angefordert"
    mitgliedskontobuchung.save()
    sende_email_an_vorstand(mitglied, mitgliedskontobuchung)

    return render(request, 'mitgliedskonto/request_spendenbescheinigung.html', {})


def sende_email_an_vorstand(mitglied, mitgliedskontobuchung):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:

        betrefftemplate = "Spendenbescheinigung angefordert"
        template = """Eine Spendenbescheinigung wurde angefordert

Name: {name}
Mitgliedsnummer: {mitgliedsnummer}
Betrag: {betrag} €
Buchungs-Datum: {buchungsdatum}
Buchungs-ID: {buchung}

Gehe zu https://alumni.bwinf.de/konto/{mitgliedsnummer} um die Bescheinigung zu erstellen und zu verifizieren.

"""

        data = {'name': mitglied.vorname + " " + mitglied.nachname,
                'vorname': mitglied.vorname,
                'nachname': mitglied.nachname,
                'anrede': mitglied.anrede,
                'mitgliedsnummer': mitglied.mitgliedsnummer,
                'datum': str(date.today()),
                'mitgliedsbeitrag': mitglied.beitrag_cent / 100.0,
                'email': mitglied.email,
                'betrag': mitgliedskontobuchung.cent_wert / 100.0,
                'buchungsdatum': mitgliedskontobuchung.buchungsdatum,
                'buchung': mitgliedskontobuchung.pk,
                }

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
            f.write("ERROR: Could not send mail to: vorstand@alumni.bwinf.de (" + str(date.today()) + ": " + betreff + ")\n\n")

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def bescheinigung_erstellen(request, mitgliedsnummer, mitgliedskontobuchungsnummer):
    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)
    mitgliedskontobuchung = get_object_or_404(MitgliedskontoBuchung, pk = mitgliedskontobuchungsnummer)
    if mitglied != mitgliedskontobuchung.mitglied:
        raise Http404("Buchung nicht gefunden.")

    if mitgliedskontobuchung.beleg_status != "angefordert" and mitgliedskontobuchung.beleg_status != "erstellt" and mitgliedskontobuchung.beleg_status != "":
        raise Http404("Buchung nicht gefunden.")

    mitgliedskontobuchung.beleg_status = "erstellt"
    mitgliedskontobuchung.save()

    bescheide = Freistellungsbescheid.objects.order_by("datum").reverse()
    bescheid = bescheide[0]

    # Important: JSON-encode user controlled data here, as we will just dump them into a JSON object in the template
    return render(request, 'mitgliedskonto/create_spendenbescheinigung.html', {
        'name': json.dumps(mitglied.vorname + " " + mitglied.nachname),
        'vorname': json.dumps(mitglied.vorname),
        'nachname': json.dumps(mitglied.nachname),
        'anrede': json.dumps(mitglied.anrede),
        'strasse': json.dumps(mitglied.strasse + ("" if mitglied.adresszusatz == "" else " " + adresszusatz)),
        'plz': json.dumps(mitglied.plz),
        'stadt': json.dumps(mitglied.stadt),
        'mitgliedsnummer': mitglied.mitgliedsnummer,
        'datum': date.today(),
        'mitgliedsbeitrag': mitglied.beitrag_cent / 100.0,
        'betrag_cent': mitgliedskontobuchung.cent_wert,
        'buchungsdatum': mitgliedskontobuchung.buchungsdatum,
        'buchung': mitgliedskontobuchung.pk,
        'bescheid': bescheid,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def bescheinigung_verifizieren(request, mitgliedsnummer, mitgliedskontobuchungsnummer):
    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)
    mitgliedskontobuchung = get_object_or_404(MitgliedskontoBuchung, pk = mitgliedskontobuchungsnummer)
    if mitglied != mitgliedskontobuchung.mitglied:
        raise Http404("Buchung nicht gefunden.")

    if mitgliedskontobuchung.beleg_status != "erstellt":
        raise Http404("Buchung nicht gefunden.")

    if not os.path.isfile(settings.BWINFALUMNI_INVOICE_DIR + str(mitglied.mitgliedsnummer) + '_' + str(mitgliedskontobuchung.pk) + '.pdf'):
        raise Http404("Datei nicht vorhanden.")

    mitgliedskontobuchung.beleg_status = "verifiziert"
    mitgliedskontobuchung.save()
    sende_email_an_mitglied(mitglied, mitgliedskontobuchung)

    return render(request, 'mitgliedskonto/verify_spendenbescheinigung.html', {})


def sende_email_an_mitglied(mitglied, mitgliedskontobuchung):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + 'spendenbescheinigung.txt', 'r', encoding='utf8') as templatefile:
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
                    'email': mitglied.email,
                    'betrag': mitgliedskontobuchung.cent_wert / 100.0,
                    'buchungsdatum': mitgliedskontobuchung.buchungsdatum,
                    'buchung': mitgliedskontobuchung.pk,
                    }

            betreff = "BWINF Alumni und Freunde e.V.: Spendenbescheinigung erstellt".format(**data)
            text = template.format(**data)

            try:
                send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [mitglied.email])
                f.write("Date: " + str(date.today()) + "\n")
                f.write("To: " + mitglied.email + "\n")
                f.write("From: vorstand@alumni.bwinf.de\n")
                f.write("Subject: " + betreff + "\n\n")
                f.write(text + "\n\n")
                return True
            except:
                f.write("ERROR: Could not send mail to: " + mitglied.email + "(" + str(date.today()) + ": " + betreff + ") \n\n")
    return False


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


class BeitraegeForm(ModelForm):
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['kommentar', 'buchungsdatum']

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
            try:
                typ = MitgliedskontoBuchungstyp.objects.filter(typname="Mitgliedsbeitrag")[0]
            except:
                typ = MitgliedskontoBuchungstyp.objects.create(typname="Mitgliedsbeitrag")
            today = date.today()
            mitglieder = Mitglied.objects.filter(beitrittsdatum__lte = today).exclude(austrittsdatum__lte = today)
            numBeitraege = 0
            for mitglied in mitglieder:
                buchung = MitgliedskontoBuchung(mitglied = mitglied,
                                                typ = typ,
                                                cent_wert = -mitglied.beitrag_cent,
                                                kommentar = bform.cleaned_data['kommentar'],
                                                buchungsdatum = bform.cleaned_data['buchungsdatum'])
                buchung.save()
                numBeitraege += 1

        if errormessage == "":
            successmessage = "Beitraeg von " + str(numBeitraege) + " Mitgliedern wurden erfolgreich abgebucht."

        return render(request, 'mitgliedskonto/adddone.html', {'errormessage': errormessage,
                                                           'successmessage': successmessage,})
    else:
        return render(request, 'mitgliedskonto/beitraege.html', {'bform': BeitraegeForm({'kommentar': "Mitgliedsbeitrag " + str(date.today().year),
                                                                                     'buchungsdatum': date.today()})})


class EmailForm(forms.Form):
    betreff = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    schulden_betrag_cent = forms.IntegerField()

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def zahlungsaufforderungen(request, templatename, schulden):
    if request.method == 'POST':
        cform = EmailForm(request.POST)

        errormessage = ""
        successmessage = ""

        if not cform.is_valid():
            errormessage = "Es müssen Text, Titel und ggf. Betrag angegeben werden. " + mform.errors.as_json(escape_html=True)
        else:
            today = date.today()
            schulden_betrag_cent = cform.cleaned_data['schulden_betrag_cent']
            mitglieder = Mitglied.objects.filter(beitrittsdatum__lte = today).exclude(austrittsdatum__lte = today)
            numEmails = 0
            failEmails = 0
            with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
                for mitglied in mitglieder:
                    kontostand = 0
                    buchungen = mitglied.mitgliedskontobuchung_set.filter(wirksam=True)
                    for buchung in buchungen:
                        kontostand += buchung.cent_wert
                    if kontostand < schulden_betrag_cent or not schulden:
                        gueltige_lastschriftmandate = mitglied.gekuerzteslastschriftmandat_set.filter(gueltig_ab__lte=today).exclude(gueltig_bis__lte=today)
                        if len(gueltige_lastschriftmandate) > 0:
                            mandat = gueltige_lastschriftmandate[0]
                            lastschrift_vorhanden = "JA"
                            lastschrift_info = "IBAN: " + mandat.iban[0:9] + " … (" + mandat.bankname + ")\n"
                        else:
                            lastschrift_vorhanden = "NEIN"
                            lastschrift_info = ""

                        data = {'vorname': mitglied.vorname,
                                'nachname': mitglied.nachname,
                                'anrede': mitglied.anrede,
                                'mitgliedsnummer': mitglied.mitgliedsnummer,
                                'datum': str(date.today()),
                                'kontostand': "{:.2f}".format(kontostand / 100.0),
                                'schulden': "{:.2f}".format(-kontostand / 100.0),
                                'email': mitglied.email,
                                'lastschrift_vorhanden': lastschrift_vorhanden,
                                'lastschrift': lastschrift_info,
                                }
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

        return render(request, 'mitgliedskonto/adddone.html', {'errormessage': errormessage,
                                                           'successmessage': successmessage,})
    else:
        template = ""
        with open(settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + templatename + ".txt", "r", encoding='utf8') as templatefile:
            for line in templatefile.readlines():   # Remove first two character of every line if they are spaces
                template += line[2:] if line[:2] == "  " else line   # Allows for templates in dokuwiki syntax …
        return render(request, 'mitgliedskonto/email.html', {'cform': EmailForm({'betreff': "Mitgliedsbeitrag BwInf Alumni und Freunde e. V.",
                                                                                 'text': template,
                                                                                 'schulden_betrag_cent': -1000}), 'schulden': schulden})




# TODO: Adding members / users should be done in 'mitgliederverwaltung' or in its own app

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
    if not settings.DEBUG:
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
        return render(request, 'mitgliedskonto/adddone.html', {'errormessage': errormessage,
                                                           'successmessage': successmessage,})

    else: # GET or something
        hochste_mitgliedernummer = Mitglied.objects.order_by('mitgliedsnummer').reverse()[0].mitgliedsnummer;
        return render(request, 'mitgliedskonto/addform.html', {'mform': MitgliedForm({'mitgliedsnummer': hochste_mitgliedernummer + 1,
                                                                                  'beitrittsdatum': date.today()}),
                                                           'pform': AddUserForm(),
                                                           'bform': UserForm()})
