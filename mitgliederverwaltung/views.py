from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
import re

from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied
from django.contrib.auth.models import User

from django import forms

from bwinfalumni.settings import DEBUG

# Keine automatisch erzeugte Form, um eigene Prüfung an benutzernamen zu implementieren und
# Djangos automatische "Benutzername existiert schon"-Kontrolle zu umgehen.
class BenutzerForm(forms.Form):
    username = forms.CharField(label='Login-Name', max_length=200)
    email    = forms.EmailField(label='Email-Adresse', max_length=200)

@login_required
def index(request):
    benutzer = request.user

    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = BenutzerForm(request.POST)
        if form.is_valid():
            if not re.compile("^\w+$").match(form.cleaned_data['username']):
                errormessage = "Der eingegebene Login-Name ist ungültig. (Alphanumerisch + Unterstrich)"
        else:
            errormessage = "Die eingegebenen Daten sind ungültig. " + form.errors.as_json(escape_html=True)
        if errormessage == "" and not benutzer.username == form.cleaned_data['username']:
            sameName = User.objects.filter(username__exact=form.cleaned_data['username'])
            if len(sameName) > 0:
                errormessage = "Dieser Login-Name existiert bereits."
        if errormessage == "":
            benutzer.username = form.cleaned_data['username']
            benutzer.email = form.cleaned_data['email']
            benutzer.save()
            successmessage = "Daten wurden erfolgreich aktualisiert."

    form = BenutzerForm({
        'username': benutzer.username,
        'email':    benutzer.email,
    })

    try:
        mitglied = benutzer.benutzermitglied.mitglied
    except:
        raise Http404("Keine Benutzerinformationen vorhanden.")

    return render(request, 'mitgliederverwaltung/uebersicht.html', {'benutzer': benutzer,
                                                        'mitglied': mitglied,
                                                        'form': form,
                                                        'errormessage': errormessage,
                                                        'successmessage': successmessage,
                                                    })



@login_required
def listusers(request):
    benutzer = request.user
    if not benutzer.is_superuser and not benutzer.groups.filter(name='vorstand').exists():
        return redirect(reverse('mitgliederverwaltung:account'))

    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')
    return render(request, 'mitgliederverwaltung/mitgliederliste.html', {'mitglieder': all_mitglieder})



@login_required
def showuser(request, userid):
    benutzer = get_object_or_404(User, id__exact = userid)
    try:
        mitglied = benutzer.benutzermitglied.mitglied
    except:
        raise Http404("Keine Benutzerinformationen vorhanden.")

    return render(request, 'mitgliederverwaltung/anzeige.html', {'benutzer': benutzer,
                                                        'mitglied': mitglied,
                                                        })



# TODO: What is actually still to be done here?

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = BenutzerMitglied
        fields = ['mitglied']

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def addbenutzer(request, mitgliedsnummer = -1):
    if not DEBUG:
        raise Http404("Benutzer-Anlegen zur Zeit noch nicht verfügbar.")

    if request.method == 'POST':
        bform = UserForm(request.POST)
        biform = UserInfoForm(request.POST)

        errormessage = ""
        successmessage = ""

        if not bform.is_valid():
            errormessage = "Die eingegebenen Daten sind ungültig. " + bform.errors.as_json(escape_html=True)
        elif not biform.is_valid():
            errormessage = "Die eingegebenen Daten sind ungültig. " + biform.errors.as_json(escape_html=True)
        else:
            bform.instance.is_staff = True
            bform.save()
            biform.instance.user = bform.instance
            biform.save()

        if errormessage == "":
            successmessage = "Benutzer wurde erfolgreich hinzugefügt."
        return render(request, 'mitgliederverwaltung/adddone.html', {'errormessage': errormessage,
                                                         'successmessage': successmessage,})
    else: # GET or something
        bform = UserForm()
        if mitgliedsnummer == -1:
            biform = UserInfoForm()
        else:
            biform = UserInfoForm({'mitglied': get_object_or_404(Mitglied, mitgliedsnummer__exact = mitgliedsnummer)})

        return render(request, 'mitgliederverwaltung/addform.html', {'bform': bform,
                                                         'biform': biform})
