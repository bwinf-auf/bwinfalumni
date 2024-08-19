from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Umsatz, Konto, UmsatzTyp
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp

from django import forms

from datetime import date, timedelta



class MitgliedskontoBuchungForm(forms.ModelForm):
    # Set form elements to not-required:
    mitglied = forms.ModelChoiceField(queryset=Mitglied.objects.all(), required=False)
    typ      = forms.ModelChoiceField(queryset=MitgliedskontoBuchungstyp.objects.all(), required=False)
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['mitglied', 'typ']
    # TODO: Add validation method that check if both of the fields are defined or none is!

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
    if request.method == 'POST':
        neu_umsatz = UmsatzForm(request.POST, prefix='umsatz')
        mkbuchung = MitgliedskontoBuchungForm(request.POST, prefix='buchung')
        if neu_umsatz.is_valid():
            if mkbuchung.data['buchung-mitglied'] or mkbuchung.data['buchung-typ']:
                if mkbuchung.is_valid():
                    umsatz = neu_umsatz.save()
                    buchung = mkbuchung.save(commit=False)
                    buchung.umsatz = umsatz
                    buchung.buchungsdatum = umsatz.wertstellungsdatum
                    buchung.cent_wert = umsatz.cent_wert
                    buchung.kommentar = umsatz.text
                    buchung.save()
                    neu_umsatz = UmsatzForm(prefix='umsatz')
                    mkbuchung = MitgliedskontoBuchungForm(prefix='buchung')
            else:
                neu_umsatz.save()
                neu_umsatz = UmsatzForm(prefix='umsatz')
                mkbuchung = MitgliedskontoBuchungForm(prefix='buchung')
        else:
            if mkbuchung.data['buchung-mitglied'] or mkbuchung.data['buchung-typ']:
                # ICH HABE KEINE IDEE, WARUM AN DIESER STELLE DAS PREFIX
                # STEHEN MUSS UND AN JEDER ANDEREN STELLE NICHT … ABER SO
                # FUNKTIONIERT ES
                pass
            else:
                mkbuchung = MitgliedskontoBuchungForm(prefix='buchung')
    else:
        neu_umsatz = UmsatzForm(prefix='umsatz')
        mkbuchung = MitgliedskontoBuchungForm(prefix='buchung')

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'geschaeftspartner')

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
    return render(request, 'umsaetze/werstellungen.html', {'umsaetze': umsaetzeinfos, 'form': neu_umsatz, 'mbform': mkbuchung})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def reportumsaetze(request, jahr):
    jahr = int(jahr)
    begin = date(jahr-1, 8, 1)
    end = date(jahr, 8, 1)
    before_end = end - timedelta(days=1)

    all_umsaetze = Umsatz.objects.select_related('konto', 'typ').order_by('wertstellungsdatum', 'geschaeftspartner')

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
                einnahmeninfos[umsatz.typ.typname] = einnahmeninfos.get(umsatz.typ.typname, 0.0) + (umsatz.cent_wert / 100.0)
                einnahmen += umsatz.cent_wert
            else:
                ausgabeninfos[umsatz.typ.typname] = ausgabeninfos.get(umsatz.typ.typname, 0.0) + (umsatz.cent_wert / 100.0)
                ausgaben += umsatz.cent_wert

    gesamt = einnahmen + ausgaben

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
                einnahmeninfos[umsatz.typ] = einnahmeninfos.get(umsatz.typ, 0.0) + (umsatz.cent_wert / 100.0)
                einnahmen += umsatz.cent_wert
            else:
                ausgabeninfos[umsatz.typ] = einnahmeninfos.get(umsatz.typ, 0.0) + (umsatz.cent_wert / 100.0)
                ausgaben += umsatz.cent_wert

    gesamt = einnahmen + ausgaben

    einnahmen = einnahmen / 100.0
    ausgaben = ausgaben / 100.0
    gesamt = gesamt / 100.0

    for typ, wert in einnahmeninfos.items():
        writer.writerow([typ, wert])

    writer.writerow(["Einnahmen Gesamt", einnahmen])

    for typ, wert in ausgabeninfos.items():
        writer.writerow([typ, wert])

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
        fields = ['typ', 'kommentar']

class MitgliedskontoBuchungEineEinzahlungForm(forms.ModelForm):
    geschaeftspartner = forms.CharField(max_length=250)

    class Meta:
        model = MitgliedskontoBuchung
        fields = ['mitglied', 'buchungsdatum', 'cent_wert']

from django.forms import formset_factory

EinzahlungenFormSet = formset_factory(MitgliedskontoBuchungEineEinzahlungForm, extra=99)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def einzahlungen(request, reverse = True):
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

                    buchung.save()

                    num += 1
            umsatzeinzahlung = UmsatzEinzahlungenForm(prefix='umsatz')
            kontoeinzahlung  = MitgliedskontoBuchungEinzahlungenForm(prefix='konto')
            einzahlungen     = EinzahlungenFormSet(prefix='einzahlungen')
    else:
        umsatzeinzahlung = UmsatzEinzahlungenForm(prefix='umsatz')
        kontoeinzahlung  = MitgliedskontoBuchungEinzahlungenForm(prefix='konto')
        einzahlungen     = EinzahlungenFormSet(prefix='einzahlungen')

    return render(request, 'umsaetze/einzahlungen.html', {'umsatzeinzahlung': umsatzeinzahlung, 'kontoeinzahlung': kontoeinzahlung, 'einzahlungen': einzahlungen, 'num':num})
