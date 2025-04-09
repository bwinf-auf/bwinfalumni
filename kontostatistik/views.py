from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='vorstand').exists())
def index(request):
    all_mitglieder = Mitglied.objects.order_by('mitgliedsnummer')

    values = {}
    for mitglied in all_mitglieder:
        val = 0
        for buchung in mitglied.mitgliedskontobuchung_set.filter(wirksam=True):
            val += buchung.cent_wert
        values[mitglied.mitgliedsnummer] = {'mitglied': mitglied, 'betrag': val/100.0}

    value_list = [v for v in values.values()]
    value_list = sorted(value_list, key=lambda x: x['betrag'], reverse=False)

    saldo = sum([v['betrag'] for v in value_list])

    return render(request, 'kontostatistik/kontostatistik.html', {'values': value_list, 'saldo': saldo})
