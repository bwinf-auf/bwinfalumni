from django.contrib.auth import login
from django.shortcuts import render

from .models import Passwordlesslogincode


class EmailForm(forms.Form):
    email = forms.EmailField(label='Neuer E-Mailadresse', max_length=250)

def index(request):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = EmailForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Finde User mit E-Mail

            # Versuche E-Mail zu senden

                successmessage = "E-Mail wurde an die angegebene Adresse versendet."
                errormessage = "E-Mail konnte nicht gesendet werden."
            else:
                errormessage = "E-Mailadresse nicht gefunden."
        else:
            errormessage = "Es sind Fehler aufgetreten. (S. o.)"
    else:
        form = EmailForm()

    return render(request, 'passwordlesslogin/index.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
                  })


def verifikation(request, code):
    try:
        logincode = Passwordlesslogincode.objects.get(logincode=code)
        # if valid_until gültig
            benutzer = logincode.benutzer
            login(request, benutzer)
            # redirect
        else:
            errormessage = "Dieser Link ist bereits abgelaufen."
    except ObjectDoesNotExist: # Kein Login mit diesem Code vorhanden
        errormessage = "Dieser Link ist nicht gültig."

    return render(request, 'passwordlesslogin/verifikation.html',{'errormessage': errormessage,})
