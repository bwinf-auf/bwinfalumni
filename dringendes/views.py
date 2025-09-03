from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from lastschriftmandatverwaltung.models import GekuerztesLastschriftmandat
from mitglieder.models import Mitglied, MitgliedskontoBuchung

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def index(request):
    neue_mandate = GekuerztesLastschriftmandat.objects.filter(gueltig_ab=None).filter(gueltig_bis=None).count()
    alte_mandate = GekuerztesLastschriftmandat.objects.exclude(gueltig_ab=None).exclude(gueltig_bis=None).filter(entfernt=None).count()

    angeforderte_belege = MitgliedskontoBuchung.objects.filter(beleg_status = "angefordert").count()
    erstellte_belege = MitgliedskontoBuchung.objects.filter(beleg_status = "erstellt").count()


    mitglieder = Mitglied.objects.filter(beitrittsdatum=None).filter(mitgliedskontobuchung__isnull=False).distinct()


    return render(request, 'dringendes/index.html', {'neue_mandate': neue_mandate,
                                                     'alte_mandate': alte_mandate,
                                                     'angeforderte_belege': angeforderte_belege,
                                                     'erstellte_belege': erstellte_belege,
                                                     'neue_mitglieder': len(mitglieder),
                                                     'mitglieder': mitglieder})
