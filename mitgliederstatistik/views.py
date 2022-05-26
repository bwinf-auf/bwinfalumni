from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from mitglieder.models import Mitglied

from datetime import date

@login_required
def index(request):

    today = date.today()
    n_mitglieder = Mitglied.objects.filter(beitrittsdatum__lte = today).exclude(austrittsdatum__lt = today).count()

    year = date.today().year
    begin_this_year = date(year, 1, 1) # January 1st of this year
    n_neu = Mitglied.objects.filter(beitrittsdatum__lte = today).exclude(austrittsdatum__lt = today).filter(beitrittsdatum__gte = begin_this_year).count()

    begin_before_year = date(year - 1, 1, 1) # January 1st of the year before
    n_neu_before = Mitglied.objects.filter(beitrittsdatum__lt = begin_this_year).filter(beitrittsdatum__gte = begin_before_year).count()

    begin_next_year = date(year + 1, 1, 1) # January 1st of next year
    n_kuendigung = Mitglied.objects.filter(beitrittsdatum__lte = today).exclude(austrittsdatum__lt = begin_this_year).filter(austrittsdatum__lt = begin_next_year).count()

    n_kuend_before = Mitglied.objects.filter(austrittsdatum__lt = begin_this_year).filter(austrittsdatum__gte = begin_before_year).count()


    return render(request, 'mitgliederstatistik/mitglieder.html', {'heute': today, 'jahr': year, 'mitglieder': n_mitglieder, 'neu': n_neu, 'kuendigungen': n_kuendigung, 'neu_before': n_neu_before, 'kuendigungen_before': n_kuend_before})
