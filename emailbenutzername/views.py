from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from django import forms


def index(request):
    benutzer = request.user
    benutzername = benutzer.username
    email = benutzer.email

    return render(request, 'emailbenutzername/index.html', {'benutzername': benutzername, 'email': email})


class BenutzernameForm(forms.Form):
    benutzername = forms.CharField(label='Neuer Benutzername', max_length=250)

def benutzername(request):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = BenutzernameForm(data=request.POST)
        if form.is_valid():
            benutzername = form.cleaned_data['benutzername']
            benutzer = request.user
            benutzer.username = benutzername
            benutzer.save()
            successmessage = "Benutzername erfolgreich geändert."
            form = BenutzernameForm()
        else:
            errormessage = "Es sind Fehler aufgetreten. (S. o.)"
    else:
        form = BenutzernameForm()

    return render(request, 'emailbenutzername/benutzername.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
                  })


class EmailForm(forms.Form):
    email = forms.EmailField(label='Neuer E-Mailadresse', max_length=250)
    password = forms.CharField(label='Passwort', max_length=250, widget=forms.PasswordInput)

    password.widget.attrs.update({'autocomplete':'new-password'})


def email(request):
    errormessage = ""
    successmessage = ""

    if request.method == 'POST':
        form = EmailForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            benutzer = request.user
            if check_password(password, benutzer.password):
                benutzer.email = email
                benutzer.save()
                try:
                    mitglied = benutzer.benutzermitglied.mitglied
                    mitglied.email = email
                    mitglied.save()
                except:
                    pass
                successmessage = "E-Mailadresse erfolgreich geändert."
                form = EmailForm()
            else:
                errormessage = "Passwort inkorrekt"
        else:
            errormessage = "Es sind Fehler aufgetreten. (S. o.)"
    else:
        form = EmailForm()

    return render(request, 'emailbenutzername/email.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage,
                  })
