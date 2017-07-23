from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Umsatz
from mitglieder.models import MitgliedskontoBuchung

from django import forms



class MitgliedskontoBuchungForm(forms.ModelForm):
    class Meta:
        model = MitgliedskontoBuchung
        fields = ['mitglied', 'typ']

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
                if neu_umsatz.is_valid():
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

