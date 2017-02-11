from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Umsatz

from django import forms

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class UmsatzForm(forms.ModelForm):
    class Meta:
        model = Umsatz
        fields = ['typ', 'text', 'centValue', 'wertstellungsDatum']

@login_required
@user_passes_test(lambda u: u.is_superuser)
def listumsaetze(request, reverse = True):
    if request.method == 'POST':
        inform = UmsatzForm(request.POST)
        inform.save()
  
    all_umsaetze = Umsatz.objects.order_by('wertstellungsDatum')
        
    current_val = 0;
    
    umsaetzeinfos = []
    for umsatz in all_umsaetze:
        
        umsaetzeinfos.append({'umsatz': umsatz,
                              'before': current_val / 100.0,
                              'after':  (current_val+umsatz.centValue) / 100.0 , 
                              'amount': umsatz.centValue / 100.0,})   
        current_val += umsatz.centValue
        
    if reverse:
        umsaetzeinfos.reverse()  
    return render(request, 'umsaetze/werstellungen.html', {'umsaetze': umsaetzeinfos, 'form': UmsatzForm()})
