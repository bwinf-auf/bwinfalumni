from django.shortcuts import render

from django.forms import ModelForm
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Verein
from mitglieder.models import Mitglied

class VereinForm(ModelForm):
    class Meta:
        model = Verein
        fields = ["beschlussfassung", "mitgliedsbeitrag_cent"]

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def index(request):
    if request.method == 'POST':
        beschlussform = VereinForm(request.POST)
        if beschlussform.is_valid():
            beschluss = beschlussform.save()

            if beschluss.mitgliedsbeitrag_cent != None:
                Mitglied.objects.filter(foerdermitglied=False).update(beitrag_cent=beschluss.mitgliedsbeitrag_cent)

    beschluesse = Verein.objects.all()
    beschluss = VereinForm()

    return render(request, 'verein/index.html', {'beschluesse': beschluesse, 'beschluss': beschluss})
