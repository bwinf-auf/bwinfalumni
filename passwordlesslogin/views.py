from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django import forms

from .models import Passwordlesslogincode
from mitglieder.models import Mitglied

from random import choice
from datetime import date, timedelta





class EmailForm(forms.Form):
    email = forms.EmailField(label='E-Mailadresse', max_length=250)

def index(request):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = EmailForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            benutzer = None

            # Nimm erstbesten Benutzer von erstbestem Mitglied
            for mitglied in Mitglied.objects.filter(email=email):
                for benutzermitglied in mitglied.benutzermitglied_set.all():
                    benutzer = benutzermitglied.benutzer
                    break

            # Überschreibe mit erstbestem Benutzer, wenn Benutzer mit E-Mail existiert
            for user in User.objects.filter(email=email):
                benutzer = user
                break

            if benutzer != None:
                logincode = ''.join(choice("ABCDEFGHKMNPQRSTUVWXYZ23456789") for _ in range(32))
                valid_until = timezone.now() + timedelta(hours=2) # Zwei Stunden gültig
                Passwordlesslogincode.objects.create(benutzer=benutzer, logincode=logincode, valid_until=valid_until)
                if sende_email_mit_logincode(email, logincode):
                    successmessage = "E-Mail wurde an die angegebene Adresse versendet."
                else:
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
        if logincode.valid_until > timezone.now():
            benutzer = logincode.benutzer
            login(request, benutzer, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
        else:
            errormessage = "Dieser Link ist bereits abgelaufen."
    except ObjectDoesNotExist:
        errormessage = "Dieser Link ist nicht gültig."

    return render(request, 'passwordlesslogin/verifikation.html',{'errormessage': errormessage,})


def sende_email_mit_logincode(email, code):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:
        with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + 'logincode.txt', 'r', encoding='utf8') as templatefile:
            template = ""
            for line in templatefile.readlines():   # Remove first two character of every line if they are spaces
                template += line[2:] if line[:2] == "  " else line   # Allows for templates in dokuwiki syntax …
            data = {'code': code}
            betreff = "E-Mail-Login BwInf Alumni und Freunde e. V.".format(**data)
            text = template.format(**data)

            try:
                send_mail(betreff, text, 'vorstand@alumni.bwinf.de', [email])
                f.write("Date: " + str(date.today()) + "\n")
                f.write("To: " + mitgliedschaftsantrag.email + "\n")
                f.write("From: vorstand@alumni.bwinf.de\n")
                f.write("Subject: " + betreff + "\n\n")
                f.write(text + "\n\n")
                return True
            except:
                f.write("ERROR: Could not send mail to: " + email + "(" + str(date.today()) + ": " + betreff + ") (logincode: " + code + ")\n\n")
    return False
