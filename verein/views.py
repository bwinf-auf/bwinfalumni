from django.shortcuts import render
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Verein, Freistellungsbescheid
from mitglieder.models import Mitglied

class VereinForm(ModelForm):
    class Meta:
        model = Verein
        fields = ["beschlussfassung", "vorstand1", "vorstand2", "mitgliedsbeitrag_cent"]

class FreistellungsbescheidForm(ModelForm):
    class Meta:
        model = Freistellungsbescheid
        fields = ["datum", "finanzamt", "steuernummer", "zeitraum"]

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def index(request):
    if request.method == 'POST':
        beschlussform = VereinForm(request.POST)
        if beschlussform.is_valid():
            if beschlussform.cleaned_data['mitgliedsbeitrag_cent'] != None or beschlussform.cleaned_data['vorstand1'] != "" or beschlussform.cleaned_data['vorstand2'] != "":
                beschluss = beschlussform.save()

                if beschluss.mitgliedsbeitrag_cent != None:
                    Mitglied.objects.filter(foerdermitglied=False).update(beitrag_cent=beschluss.mitgliedsbeitrag_cent)

        bescheidform = FreistellungsbescheidForm(request.POST)
        if bescheidform.is_valid():
            bescheid = bescheidform.save()

    beschluesse = Verein.objects.order_by("beschlussfassung")
    beschluss = VereinForm()

    bescheide = Freistellungsbescheid.objects.order_by("datum")
    bescheid = FreistellungsbescheidForm()

    return render(request, 'verein/index.html', {'beschluesse': beschluesse, 'beschluss': beschluss, 'bescheide': bescheide, 'bescheid': bescheid})
