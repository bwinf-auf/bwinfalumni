from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Umsatz, Konto, UmsatzTyp
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp

from django import forms

from datetime import date, timedelta


class UmsatzForm(forms.ModelForm):
    class Meta:
        model = Umsatz
        fields = ['konto', 'typ', 'text', 'cent_wert', 'beleg', 'author', 'geschaeftspartner', 'wertstellungsdatum', 'kommentar']

    def __init__(self, *args, **kwargs):
        super(UmsatzForm, self).__init__(*args, **kwargs)
        self.fields['wertstellungsdatum'].widget.attrs['style'] = 'width:100px;'
        self.fields['cent_wert'].widget.attrs['style'] = 'width:80px;'
        self.fields['text'].widget.attrs['style'] = 'width:300px;'
        self.fields['beleg'].widget.attrs['style'] = 'width:200px;'
        self.fields['author'].widget.attrs['style'] = 'width:200px;'
        self.fields['geschaeftspartner'].widget.attrs['style'] = 'width:200px;'
        self.fields['kommentar'].widget.attrs['style'] = 'width:200px;'


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def listumsaetze(request, reverse = True):
    try:
        mitglied = request.user.benutzermitglied.mitglied
        autor = mitglied.vorname + " " + mitglied.nachname
    except:
        autor = None

    try:
        girokonto = Konto.objects.get(kontoname="Girokonto")
    except:
        girokonto = None

    if request.method == 'POST':
        neu_umsatz = UmsatzForm(request.POST, prefix='umsatz')
        if neu_umsatz.is_valid():
            neu_umsatz.save()
            neu_umsatz = UmsatzForm(
                prefix='umsatz',
                initial={
                    'author': autor,
                    'konto': girokonto,
                },
            )
    else:
        neu_umsatz = UmsatzForm(
            prefix='umsatz',
            initial={
                'author': autor,
                'konto': girokonto,
            },
        )

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'sortierhinweis', 'geschaeftspartner')

    current_val = 0;

    umsaetzeinfos = []
    for umsatz in all_umsaetze:

        umsaetzeinfos.append({'umsatz': umsatz,
                              'before': current_val / 100.0,
                              'after':  (current_val+umsatz.cent_wert) / 100.0 ,
                              'amount': umsatz.cent_wert / 100.0,})
        current_val += umsatz.cent_wert

    if reverse:
        umsaetzeinfos.reverse()
    return render(request, 'umsaetze/werstellungen.html', {'umsaetze': umsaetzeinfos, 'form': neu_umsatz})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def reportumsaetze(request, jahr):
    jahr = int(jahr)
    begin = date(jahr-1, 8, 1)
    end = date(jahr, 8, 1)
    before_end = end - timedelta(days=1)

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'sortierhinweis', 'geschaeftspartner')

    current_val = 0

    umsaetzeinfos = []
    for umsatz in all_umsaetze:
        if umsatz.wertstellungsdatum >= begin and umsatz.wertstellungsdatum < end:
            umsaetzeinfos.append({'umsatz': umsatz,
                                  'before': current_val / 100.0,
                                  'after':  (current_val+umsatz.cent_wert) / 100.0 ,
                                  'amount': umsatz.cent_wert / 100.0,
                                  'last': False, })
        current_val += umsatz.cent_wert

    umsaetzeinfos[-1]['last'] = True

    return render(request, 'umsaetze/kassenbuch.html', {'umsaetze': umsaetzeinfos, 'begin': begin, 'end': before_end})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def reportumsaetzecsv(request, jahr):
    import csv
    from django.http import HttpResponse
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="kasse_' + jahr + '.csv"'

    writer = csv.writer(response)
    writer.writerow(["Wertstellung", "Umsatz (in €)", "Kontostand (in €)", "Buchung", "Art der Buchung", "Beleg", "Geschäftspartner", "Kommentar"])

    jahr = int(jahr)
    begin = date(jahr-1, 8, 1)
    end = date(jahr, 8, 1)
    before_end = end - timedelta(days=1)

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'geschaeftspartner')

    current_val = 0

    firstumsatz = True

    umsaetzeinfos = []
    for umsatz in all_umsaetze:
        if umsatz.wertstellungsdatum >= begin and umsatz.wertstellungsdatum < end:
            if firstumsatz:
                writer.writerow(["", "", current_val / 100.0, "", "", "", "", ""])
                firstumsatz = False
            writer.writerow([umsatz.wertstellungsdatum, umsatz.cent_wert / 100.0, (current_val+umsatz.cent_wert) / 100.0, umsatz.text, umsatz.typ, umsatz.beleg, umsatz.geschaeftspartner, umsatz.kommentar])
        current_val += umsatz.cent_wert

    return response


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def report(request, jahr):
    jahr = int(jahr)
    begin = date(jahr-1, 8, 1)
    end = date(jahr, 8, 1)
    before_end = end - timedelta(days=1)

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'geschaeftspartner')

    einnahmeninfos = {}
    ausgabeninfos = {}

    einnahmen = 0
    ausgaben = 0

    for umsatz in all_umsaetze:
        if umsatz.wertstellungsdatum >= begin and umsatz.wertstellungsdatum < end:
            # TODO: Calculate with ints here?
            if umsatz.cent_wert >= 0:
                einnahmeninfos[umsatz.typ.typname] = einnahmeninfos.get(umsatz.typ.typname, 0) + umsatz.cent_wert
                einnahmen += umsatz.cent_wert
            else:
                ausgabeninfos[umsatz.typ.typname] = ausgabeninfos.get(umsatz.typ.typname, 0) + umsatz.cent_wert
                ausgaben += umsatz.cent_wert

    gesamt = einnahmen + ausgaben

    einnahmeninfos = {key: value / 100.0 for key, value in einnahmeninfos.items()}
    ausgabeninfos = {key: value / 100.0 for key, value in ausgabeninfos.items()}

    einnahmen = einnahmen / 100.0
    ausgaben = ausgaben / 100.0
    gesamt = gesamt / 100.0

    return render(request, 'umsaetze/bericht.html', {'einnahmen': einnahmeninfos, 'ausgaben': ausgabeninfos, 'geseinnahmen': einnahmen, 'gesausgaben': ausgaben, 'gesamt': gesamt, 'begin': begin, 'end': before_end})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def reportcsv(request, jahr):
    import csv
    from django.http import HttpResponse
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="bericht_' + jahr + '.csv"'

    writer = csv.writer(response)
    writer.writerow(["Typ", "Umsatz (in €)"])

    jahr = int(jahr)
    begin = date(jahr-1, 8, 1)
    end = date(jahr, 8, 1)
    before_end = end - timedelta(days=1)

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'geschaeftspartner')

    einnahmeninfos = {}
    ausgabeninfos = {}

    einnahmen = 0
    ausgaben = 0

    for umsatz in all_umsaetze:
        if umsatz.wertstellungsdatum >= begin and umsatz.wertstellungsdatum < end:
            # TODO: Calculate with ints here?
            if umsatz.cent_wert >= 0:
                einnahmeninfos[umsatz.typ] = einnahmeninfos.get(umsatz.typ, 0) + umsatz.cent_wert
                einnahmen += umsatz.cent_wert
            else:
                ausgabeninfos[umsatz.typ] = ausgabeninfos.get(umsatz.typ, 0) + umsatz.cent_wert
                ausgaben += umsatz.cent_wert

    gesamt = einnahmen + ausgaben

    einnahmen = einnahmen / 100.0
    ausgaben = ausgaben / 100.0
    gesamt = gesamt / 100.0

    for typ, wert in einnahmeninfos.items():
        writer.writerow([typ, wert / 100.0])

    writer.writerow(["Einnahmen Gesamt", einnahmen])

    for typ, wert in ausgabeninfos.items():
        writer.writerow([typ, wert / 100.0])

    writer.writerow(["Ausgaben Gesamt", ausgaben])
    writer.writerow(["Total", gesamt])

    return response


class UmsatzEinzahlungenForm(forms.ModelForm):
    text = forms.CharField(max_length=250, initial="Mitglied {mitgliedsnummer} ({vorname_initiale}. {nachname}): Beitragszahlung")

    class Meta:
        model = Umsatz
        fields = ['konto', 'typ', 'beleg', 'author']

class MitgliedskontoBuchungEinzahlungenForm(forms.ModelForm):
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['typ', 'kommentar', 'wirksam']

class MitgliedskontoBuchungEineEinzahlungForm(forms.ModelForm):
    geschaeftspartner = forms.CharField(max_length=250)

    class Meta:
        model = MitgliedskontoBuchung
        fields = ['mitglied', 'buchungsdatum', 'cent_wert']

    field_order = ['mitglied', 'geschaeftspartner', 'buchungsdatum', 'cent_wert']


from django.forms import formset_factory

EinzahlungenFormSet = formset_factory(MitgliedskontoBuchungEineEinzahlungForm, extra=99)


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def einzahlungen(request, reverse = True):
    try:
        mitglied = request.user.benutzermitglied.mitglied
        autor = mitglied.vorname + " " + mitglied.nachname
    except:
        autor = None

    try:
        girokonto = Konto.objects.get(kontoname="Girokonto")
    except:
        girokonto = None

    try:
        umsatztyp = UmsatzTyp.objects.get(typname="Beitraege")
    except:
        umsatztyp = None

    try:
        buchungstyp = MitgliedskontoBuchungstyp.objects.get(typname="Beitragszahlung")
    except:
        buchungstyp = None


    num = 0
    if request.method == 'POST':
        umsatzeinzahlung = UmsatzEinzahlungenForm(request.POST, prefix='umsatz')
        kontoeinzahlung  = MitgliedskontoBuchungEinzahlungenForm(request.POST, prefix='konto')
        einzahlungen     = EinzahlungenFormSet(request.POST, prefix='einzahlungen')
        if umsatzeinzahlung.is_valid() and kontoeinzahlung.is_valid() and einzahlungen.is_valid():
            for form in einzahlungen.forms:
                if form.has_changed():
                    mitglied = form.cleaned_data['mitglied']

                    data = {'vorname': mitglied.vorname,
                            'vorname_initiale': mitglied.vorname[0:1] or "?",
                            'nachname': mitglied.nachname,
                            'nachname_initiale': mitglied.nachname[0:1] or "?",
                            'anrede': mitglied.anrede,
                            'mitgliedsnummer': mitglied.mitgliedsnummer,
                            'datum': str(date.today()),
                            'email': mitglied.email}
                    text = umsatzeinzahlung.cleaned_data['text'].format(**data)

                    umsatz = Umsatz()

                    buchung = MitgliedskontoBuchung()

                    umsatz.konto               = umsatzeinzahlung.cleaned_data['konto']
                    umsatz.typ                 = umsatzeinzahlung.cleaned_data['typ']
                    umsatz.text                = text
                    umsatz.cent_wert           = form.cleaned_data['cent_wert']
                    umsatz.beleg               = umsatzeinzahlung.cleaned_data['beleg']
                    umsatz.author              = umsatzeinzahlung.cleaned_data['author']
                    umsatz.geschaeftspartner   = form.cleaned_data['geschaeftspartner']
                    umsatz.wertstellungsdatum  = form.cleaned_data['buchungsdatum']

                    umsatz.save()

                    buchung.mitglied           = mitglied
                    buchung.typ                = kontoeinzahlung.cleaned_data['typ']
                    buchung.cent_wert          = form.cleaned_data['cent_wert']
                    buchung.kommentar          = kontoeinzahlung.cleaned_data['kommentar']
                    buchung.umsatz             = umsatz
                    buchung.buchungsdatum      = form.cleaned_data['buchungsdatum']
                    buchung.wirksam            = kontoeinzahlung.cleaned_data['wirksam']

                    buchung.save()

                    num += 1

            umsatzeinzahlung = UmsatzEinzahlungenForm(
                prefix='umsatz',
                initial={
                    'beleg': 'Kontoauszug',
                    'author': autor,
                    'konto': girokonto,
                    'typ': umsatztyp,
                },
            )

            kontoeinzahlung = MitgliedskontoBuchungEinzahlungenForm(
                prefix='konto',
                initial={
                    'typ': buchungstyp,
                    'kommentar': "Beitragszahlung",
                }
            )
            einzahlungen = EinzahlungenFormSet(prefix='einzahlungen')
    else:
        umsatzeinzahlung = UmsatzEinzahlungenForm(
            prefix='umsatz',
            initial={
                'beleg': 'Kontoauszug',
                'author': autor,
                'konto': girokonto,
                'typ': umsatztyp,
            },
        )

        kontoeinzahlung = MitgliedskontoBuchungEinzahlungenForm(
            prefix='konto',
            initial={
                'typ': buchungstyp,
                'kommentar': "Beitragszahlung",
            }
        )
        einzahlungen = EinzahlungenFormSet(prefix='einzahlungen')

    return render(request, 'umsaetze/einzahlungen.html', {'umsatzeinzahlung': umsatzeinzahlung, 'kontoeinzahlung': kontoeinzahlung, 'einzahlungen': einzahlungen, 'num':num})



def erstelle_sortierhinweis(kontoauszugeintrag):
    positive = kontoauszugeintrag["amount"][0] != '-'
    amount = kontoauszugeintrag["amount"].split(".")
    euro = int(amount[0])
    cent = int(amount[1])*10 if len(amount[1]) == 1 else int(amount[1])
    betrag = 100 * euro + cent if positive else 100 * euro - cent
    umsaetze = Umsatz.objects.filter(
        wertstellungsdatum=kontoauszugeintrag["date"],
        cent_wert=betrag,
    )

    if len(umsaetze) == 0:
        return (False, "Konnte keinen potentiellen Umsatz finden für " + str(kontoauszugeintrag), False)

    if len(umsaetze) == 1:
        umsatz = umsaetze[0]
        umsatz.sortierhinweis = int(kontoauszugeintrag["order_index"])
        umsatz.save()
        return (True, "", False)

    ## Prepare for name matching:
    import re
    nameparts = [part for part in re.split(r'\W+|-', kontoauszugeintrag["partner"].lower()) if part not in ["dr.", "prof.", "und", "oder"]]

    match_umsatz = None
    for umsatz in umsaetze:
        match_name = True
        names = re.split(r'\W+|-', umsatz.geschaeftspartner.lower())
        for name in names:
            if not name in nameparts:
                match_name = False

        match_mitgliedsnummer = False
        if kontoauszugeintrag["member_id"] != None:
            mitgliedskontobuchungen = umsatz.mitgliedskontobuchung_set.all()
            if len(mitgliedskontobuchungen) == 1:

                if mitgliedskontobuchungen[1].mitglied.mitgliedsnummer == int(kontoauszugeintrag["member_id"]):
                    match_mitgliedsnummer = True
                else:
                    continue

        message = ""
        if match_mitgliedsnummer and not match_name:
            message = "Mitgliedsnummer-Match aber Diskrepanz Name: " + str(kontoauszugeintrag)

        if match_mitgliedsnummer or match_name:
            if match_umsatz is None:
                match_umsatz = umsatz
            else:
                ## Die fatally
                return (False, "FEHLER: Mehrere Einträge in Kasse passen zu Kontoauszugeintrag:" + str(kontoauszugeintrag), True)

    if match_umsatz is None:
        return (False, "Konnte keinen Umsatz finden für " + str(kontoauszugeintrag), False)

    umsatz = match_umsatz
    umsatz.sortierhinweis = int(kontoauszugeintrag["order_index"])
    umsatz.save()
    return (True, "", False)


class SortierungAendernForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea(attrs={'rows': 15, 'cols': 120}), initial="date,amount,partner,member_id,order_index")


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def sortierung_aendern(request):
    import csv

    messages = []
    n_erfolg = 0
    n_fail = 0

    if request.method == 'POST':
        sortierung_daten = SortierungAendernForm(request.POST)

        if sortierung_daten.is_valid():
            if sortierung_daten.has_changed():
                from io import StringIO
                f = StringIO(sortierung_daten.cleaned_data['data'])
                reader = csv.DictReader(f)

                fatal_error = False
                for row in reader:
                    (erfolg, message, fatal) = erstelle_sortierhinweis(row)
                    if erfolg:
                        n_erfolg += 1
                    else:
                        n_fail += 1
                    if message != "":
                        messages.append(message)
                    if fatal:
                        fatal_error = True
                        break

                if not fatal_error:
                    messages.append(str(n_erfolg) + " Einträge erfolgreich")
                    messages.append(str(n_fail) + " Einträge konnten nicht zugeordnet werden")
                    sortierung_daten = SortierungAendernForm()
    else:
        sortierung_daten = SortierungAendernForm()

    return render(request, 'umsaetze/sortierung_aendern.html', {'sortierung_daten': sortierung_daten, 'messages': messages})
