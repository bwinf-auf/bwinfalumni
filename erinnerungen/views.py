from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.forms import ModelForm
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Erinnerung, Dauer

from datetime import date
import os.path

class ErinnerungForm(ModelForm):
    class Meta:
        model = Erinnerung
        fields = ["name", "titel", "erstmals", "zuletzt", "zyklus"]

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def index(request):
    if request.method == 'POST':
        erinnerungform = ErinnerungForm(request.POST)
        if erinnerungform.is_valid():
            erinnerung = erinnerungform.save()

    erinnerungen = Erinnerung.objects.all()
    erinnerung = ErinnerungForm()

    return render(request, 'erinnerungen/index.html', {'erinnerungen': erinnerungen, 'erinnerung': erinnerung})

def nudge(request):
    erinnerungen = Erinnerung.objects.all()

    for erinnerung in erinnerungen:
        t = erinnerung.erstmals
        match erinnerung.zyklus:
            case Dauer.ZWEIJAHR:
                while t <= erinnerung.zuletzt:
                    t = t.replace(t.year + 2)
            case Dauer.JAHR:
                while t <= erinnerung.zuletzt:
                    t = t.replace(t.year + 1)
            case Dauer.HALBJAHR:
                while t <= erinnerung.zuletzt:
                    if t.month + 6 <= 12:
                        t = t.replace(t.year, t.month + 6)
                    else:
                        t = t.replace(t.year + 1, t.month + 6 - 12)
            case Dauer.QUARTAL:
                while t <= erinnerung.zuletzt:
                    if t.month + 3 <= 12:
                        t = t.replace(t.year, t.month + 3)
                    else:
                        t = t.replace(t.year + 1, t.month + 3 - 12)
            case Dauer.MONAT:
                while t <= erinnerung.zuletzt:
                    if t.month + 1 <= 12:
                        t = t.replace(t.year, t.month + 1)
                    else:
                        t = t.replace(t.year + 1, t.month + 1 - 12)
            case Dauer.VIERWOCHE:
                delta = timedelta(weeks = 4)
                while t <= erinnerung.zuletzt:
                    t = t + delta
        if t <= date.today():
            erinnerung.zuletzt = date.today()
            erinnerung.save()
            sende_email_an_vorstand(erinnerung.name, erinnerung.titel)

    return HttpResponse("Ok.")


def sende_email_an_vorstand(name, titel):
    with open(settings.BWINFALUMNI_LOGS_DIR + 'maillog', 'a', encoding='utf8') as f:

        betrefftemplate = "Erinnerung: " + titel
        template = titel

        if os.path.isfile(settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + "erinnerungen/" + name + '.txt'):
            with open (settings.BWINFALUMNI_MAIL_TEMPLATE_DIR + "erinnerungen/" + name + '.txt', 'r', encoding='utf8') as templatefile:
                template = ""
                for line in templatefile.readlines():   # Remove first two character of every line if they are spaces, allows …
                    template += line[2:] if line[:2] == "  " else line   # … for templates as codeblocks in dokuwiki syntax.

        data = {}

        betreff = betrefftemplate.format(**data)
        text = template.format(**data)

        try:
            send_mail(betreff, text, 'vorstand@alumni.bwinf.de', ['vorstand@alumni.bwinf.de'])
            f.write("Date: " + str(date.today()) + "\n")
            f.write("To: vorstand@alumni.bwinf.de\n")
            f.write("From: vorstand@alumni.bwinf.de\n")
            f.write("Subject: " + betreff + "\n\n")
            f.write(text + "\n\n")
        except:
            f.write("ERROR: Could not send mail to: vorstand@alumni.bwinf.de (" + str(date.today()) + ": " + betreff + ")\n\n")
