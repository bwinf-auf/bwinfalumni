from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Umsatz

from django import forms



class UmsatzForm(forms.ModelForm):
    class Meta:
        model = Umsatz
        fields = ['typ', 'text', 'centWert', 'wertstellungsdatum']

@login_required
@user_passes_test(lambda u: u.is_superuser)
def listumsaetze(request, reverse = True):
    if request.method == 'POST':
        inform = UmsatzForm(request.POST)
        inform.save()
  
    all_umsaetze = Umsatz.objects.order_by('wertstellungsdatum')
        
    current_val = 0;
    
    umsaetzeinfos = []
    for umsatz in all_umsaetze:
        
        umsaetzeinfos.append({'umsatz': umsatz,
                              'before': current_val / 100.0,
                              'after':  (current_val+umsatz.centWert) / 100.0 , 
                              'amount': umsatz.centWert / 100.0,})   
        current_val += umsatz.centWert
        
    if reverse:
        umsaetzeinfos.reverse()  
    return render(request, 'umsaetze/werstellungen.html', {'umsaetze': umsaetzeinfos, 'form': UmsatzForm()})
