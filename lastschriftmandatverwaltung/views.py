from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import GekuerztesLastschriftmandat
from django.contrib.auth.models import User
from mitglieder.models import Mitglied
from benutzer.models import BenutzerMitglied

from datetime import date

from django import forms
from django.shortcuts import redirect
from django.forms import ModelForm

from django.urls import reverse


@login_required
def index(request):
    benutzer = request.user

    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        try:
            mitglied = benutzer.benutzermitglied.mitglied
        except:
            raise Http404("Keine Benutzerinformationen vorhanden.")
        return redirect(reverse('lastschriftmandatverwaltung:detail', kwargs={'mitgliedsnummer':mitglied.mitgliedsnummer}))

    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')
    return render(request, 'lastschriftmandatverwaltung/mitgliederliste.html', {'mitglieder': all_mitglieder})



class GekuerztesLastschriftmandatForm(ModelForm):
    class Meta:
        model = GekuerztesLastschriftmandat
        fields = ['kontoinhaber', 'bankname', 'iban', 'bic']


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
        lsmandat = GekuerztesLastschriftmandatForm()
        # TODO Read form from POST-Data
    else:
        lsmandat = GekuerztesLastschriftmandatForm()

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
                             'gueltig_ab': "–" if mandat.gueltig_ab == None else mandat.gueltig_ab,
                             'gueltig_bis': "–" if mandat.gueltig_bis == None else mandat.gueltig_bis,
                            })
    return render(request, 'lastschriftmandatverwaltung/mitglied.html', {'mitglied': mitglied, 'mandate': alle_mandate, 'form': lsmandat})


