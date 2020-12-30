from django.shortcuts import render

from django import forms

from .models import Mitgliedschaftsantrag

class MitgliedschaftsantragForm(forms.ModelForm):
    class Meta:
        model = Mitgliedschaftsantrag
        fields = ['vorname', 'nachname', 'anrede', 'geburtsdatum', 'email', 'mitgliedschaft', 'mitgliedsbeitrag', 'strasse', 'adresszusatz', 'plz', 'stadt', 'land', 'telefon', 'beruf', 'studienort', 'studienfach', 'mailingliste', 'adresse_verein', 'adresse_bwinf', 'name_welt']
        widgets = { 'mitgliedschaft': forms.RadioSelect }
        labels = { 
            'vorname': "Vorname*",
            'nachname': "Nachname*",
            'geburtsdatum': "Geburtsdatum*",
            'email': "E-Mailadresse*",
            'mitgliedschaft': "Vereinsmitgliedschaft*",
            'strasse': "Straße, Hausnummer*",
            'plz': "Postleitzahl*",
            'stadt': "Ort*",
            
            'beruf': "Beschäftigung" }
    
def antrag(request):
    errormessage = ""
    successmessage = ""
    
    if request.method == 'POST':
        form = MitgliedschaftsantragForm(data=request.POST)
        if form.is_valid():
            form.save()
        else:
            errormessage = "Es sind Fehler aufgetreten." + str(form.errors)
    else:
        form = MitgliedschaftsantragForm()

    return render(request, 'mitgliedschaftsantrag/antrag.html',
                  {'form': form,
                   'errormessage': errormessage,
                   'successmessage': successmessage, 
                  })  
