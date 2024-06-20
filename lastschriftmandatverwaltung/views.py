from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.forms import ModelForm
from django.http import HttpResponse, Http404
from django.conf import settings
from django.urls import reverse
from django import forms

from .models import GekuerztesLastschriftmandat
from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied

from datetime import date

@login_required
def index(request):
    benutzer = request.user

    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        return redirect(reverse('lastschriftmandatverwaltung:detail', kwargs={'mitgliedsnummer':mitglied.mitgliedsnummer}))

    alle_mandate = []
    for mandat in GekuerztesLastschriftmandat.objects.order_by('gueltig_bis', 'gueltig_ab'):
        alle_mandate.append({'id': mandat.id,
                             'inhaber': mandat.kontoinhaber,
                             'bankname': mandat.bankname,
                             'iban': mandat.iban,
                             'bic': mandat.bic,
                             'referenz': mandat.referenz,
                             'gueltig': False if mandat.gueltig_ab == None else
                                        False if mandat.gueltig_ab > date.today() else
                                        True if mandat.gueltig_bis == None else
                                        True if mandat.gueltig_bis > date.today() else
                                        False,
                             'neu': False if mandat.gueltig_ab != None else
                                    False if mandat.gueltig_bis != None else
                                    True,
                             'erstellung': "–" if mandat.erstellung == None else mandat.erstellung,
                             'gueltig_ab': "–" if mandat.gueltig_ab == None else mandat.gueltig_ab,
                             'gueltig_bis': "–" if mandat.gueltig_bis == None else mandat.gueltig_bis,
                            })

    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')
    return render(request, 'lastschriftmandatverwaltung/mitgliederliste.html', {'mitglieder': all_mitglieder, 'mandate': alle_mandate})

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

    alle_mandate = []
    for mandat in mitglied.gekuerzteslastschriftmandat_set.all():
        alle_mandate.append({'id': mandat.id,
                             'inhaber': mandat.kontoinhaber,
                             'bankname': mandat.bankname,
                             'iban': mandat.iban,
                             'bic': mandat.bic,
                             'referenz': mandat.referenz,
                             'gueltig': False if mandat.gueltig_ab == None else
                                        False if mandat.gueltig_ab > date.today() else
                                        True if mandat.gueltig_bis == None else
                                        True if mandat.gueltig_bis > date.today() else
                                        False,
                             'neu': False if mandat.gueltig_ab != None else
                                    False if mandat.gueltig_bis != None else
                                    True,
                             'gueltig_ab': "–" if mandat.gueltig_ab == None else mandat.gueltig_ab,
                             'gueltig_bis': "–" if mandat.gueltig_bis == None else mandat.gueltig_bis,
                            })
    return render(request, 'lastschriftmandatverwaltung/mitglied.html', {'mitglied': mitglied, 'mandate': alle_mandate})


class GekuerztesLastschriftmandatForm(ModelForm):
    class Meta:
        model = GekuerztesLastschriftmandat
        fields = ['kontoinhaber', 'anschrift', 'bankname', 'bic', 'iban']
        labels = {
            'kontoinhaber': "Kontoinhaber (Vor- und Nachname)",
            'anschrift': "Anschrift (Straße, Hausnummer, Postleitzahl, Ort)",
            'bankname': "Name der Bank / des Kreditinstituts",
            'bic': "BIC",
            'iban': "IBAN",
            }

class EmptyForm(forms.Form):
    pass

def iban_valid(iban):
    # From https://codereview.stackexchange.com/questions/135366/python-iban-validation
    iban = iban.upper().replace(" ", "")
    import string
    letters = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}
    return int((iban[4:] + iban[:4]).translate(letters)) % 97 == 1

@login_required
def addnew(request, mitgliedsnummer):
    benutzer = request.user

    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        if mitglied.mitgliedsnummer != int(mitgliedsnummer):
            raise Http404("Kein Zugriff (" + str(mitglied.mitgliedsnummer) + ")")

    mitglied = get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)

    errormessage = ""

    if request.method == 'POST':
        lsmandat = GekuerztesLastschriftmandatForm(request.POST)
        if not lsmandat.is_valid():
            errormessage = "Die eingegebenen Daten sind ungültig. " + lsmandat.errors.as_json(escape_html=True)
        else:
            mandat = lsmandat.save(commit=False)
            mandat.mitglied = mitglied
            mandat.erstellung = date.today()

            if not iban_valid(mandat.iban):
                errormessage = "IBAN ungültig oder IBAN-Format unbekannt. Bitte versuche es erneut oder wende dich an vorstand@alumni.bwinf.de, wenn das Problem andauert."
            else:
                iban = mandat.iban.replace(" ", "")
                iban_starred = iban[0:8] + ("*" * (len(iban)-8))
                iban_spaced = " ".join(iban[i:i+4] for i in range(0, len(iban), 4))
                iban_starred = " ".join(iban_starred[i:i+4] for i in range(0, len(iban), 4))
                mandat.iban = iban_starred
                try:
                    with open(settings.BWINFALUMNI_LOGS_DIR + 'mandatlog', 'a', encoding='utf8') as mandatlog:
                        mandatlog.write("M" + str(mitglied.mitgliedsnummer) + " ADD IBAN: " + iban_spaced + "\n")
                        mandat.save()
                except:
                    errormessage = "Serverfehler: Mandat konnte nicht eingetragen werden. Bitte versuche es erneut oder wende dich an vorstand@alumni.bwinf.de, wenn das Problem andauert."
    else:
        lsmandat = GekuerztesLastschriftmandatForm(initial={'kontoinhaber': mitglied.vorname + " " + mitglied.nachname})

    if request.method == 'POST' and errormessage == "":
        return redirect(reverse('lastschriftmandatverwaltung:detail', kwargs={'mitgliedsnummer':mitglied.mitgliedsnummer}))
    else:
        return render(request, 'lastschriftmandatverwaltung/addnew.html', {'mitglied': mitglied, 'form': lsmandat,
                                                                           'errormessage': errormessage,})


@login_required
def delete(request, lastschriftmandat_id):
    benutzer = request.user

    lsm = get_object_or_404(GekuerztesLastschriftmandat, id__exact = lastschriftmandat_id)

    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        if mitglied.mitgliedsnummer != lsm.mitglied.mitgliedsnummer:
            raise Http404("Kein Zugriff (" + str(mitglied.mitgliedsnummer) + ")")

    mitglied = lsm.mitglied

    if request.method == 'POST':
        empty = EmptyForm(request.POST)
        if empty.is_valid():
            if lsm.gueltig_bis == None:
                lsm.gueltig_bis = date.today()
                lsm.save()
                try:
                    with open(settings.BWINFALUMNI_LOGS_DIR + 'mandatlog', 'a', encoding='utf8') as mandatlog:
                        mandatlog.write("M" + str(mitglied.mitgliedsnummer) + " REMOVE IBAN: " + lsm.iban + "\n")
                        mandat.save()
                except:
                    pass

    return redirect(reverse('lastschriftmandatverwaltung:detail', kwargs={'mitgliedsnummer':mitglied.mitgliedsnummer}))


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def accept(request, lastschriftmandat_id):
    benutzer = request.user

    lsm = get_object_or_404(GekuerztesLastschriftmandat, id__exact = lastschriftmandat_id)

    mitglied = lsm.mitglied

    if request.method == 'POST':
        empty = EmptyForm(request.POST)
        if empty.is_valid():
            if lsm.gueltig_ab == None:
                for refnr in range(1,1000): # find unused reference number … give up at 999
                    ref = "{:0>4}".format(mitglied.mitgliedsnummer) + "-" + str(refnr)
                    if not GekuerztesLastschriftmandat.objects.filter(referenz=ref).exists():
                        lsm.referenz = ref
                        sende_email_mit_mandatsreferenz(mitglied, ref)
                        break
                for altmandat in mitglied.gekuerzteslastschriftmandat_set.all():
                    if altmandat.gueltig_ab != None and altmandat.gueltig_bis == None:
                        altmandat.gueltig_bis = date.today()
                        altmandat.save()
                lsm.gueltig_ab = date.today()
                lsm.save()

    return redirect(reverse('lastschriftmandatverwaltung:index'))




def sende_email_mit_mandatsreferenz(mitglied, mandatsreferenz):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + 'lastschriftmandat.txt', 'r', encoding='utf8') as templatefile:
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
                    'mandatsreferenz': mandatsreferenz,
                    'email': mitglied.email}
            betreff = "Lastschriftmandat für den BwInf Alumni und Freunde e. V.".format(**data)
            text = template.format(**data)

            try:
                send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [mitglied.email])
                f.write("Date: " + str(date.today()) + "\n")
                f.write("To: " + mitglied.email + "\n")
                f.write("From: vorstand@alumni.bwinf.de\n")
                f.write("Subject: " + betreff + "\n\n")
                f.write(text + "\n\n")
            except:
                f.write("ERROR: Could not send mail to: " + mitglied.email + "(" + str(date.today()) + ": " + betreff + ") (Mandat: " + mandatsreferenz + ")\n\n")
