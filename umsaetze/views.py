from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Umsatz, Konto, UmsatzTyp
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp

from django import forms

from datetime import date



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
  
    all_umsaetze = Umsatz.objects.order_by('wertstellungsdatum')
        
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
