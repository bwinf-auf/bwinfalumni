from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp, Lastschriftmandat
from umsaetze.models import Umsatz, UmsatzTyp, Konto



def erstelle_mockdaten():
    testusers = [
        User.objects.create_user('test', 'test@example.com', 'test', is_staff=True),
        User.objects.create_user('max', 'max@example.com', 'max', is_staff=True),
        User.objects.create_user('willi', 'willi@example.com', 'willi', is_staff=True),
        User.objects.create_user('williadmin', 'willi@example.com', 'willi', is_staff=True),
        User.objects.create_user('nico', 'nico@example.com', 'nico', is_staff=True),
        ]
    
    testmitglieder = [
        Mitglied(mitgliedsnummer=99927, vorname="Test", nachname="Testofsky", strasse="Str", plz="12343", stadt="B.", telefon="0", email="test@example.com"),
        Mitglied(mitgliedsnummer=99928, vorname="Max", nachname="Mustermann", strasse="Str", plz="12343", stadt="B.", telefon="0", email="max@example.com"),
        Mitglied(mitgliedsnummer=99929, vorname="Willi", nachname="Vanilly", strasse="Str", plz="12343", stadt="B.", telefon="0", email="willi@example.com"),
        Mitglied(mitgliedsnummer=99930, vorname="Lena", nachname="Lane", strasse="Str", plz="12343", stadt="B.", telefon="0", email="lena@example.com"),
        ]
    
    bm = [
        BenutzerMitglied(benutzer=testusers[0], mitglied=testmitglieder[0]),
        BenutzerMitglied(benutzer=testusers[1], mitglied=testmitglieder[1]),
        BenutzerMitglied(benutzer=testusers[2], mitglied=testmitglieder[2]),
        BenutzerMitglied(benutzer=testuser[3], mitglied=testmitglieder[2]),
        ]
    
    konto = Konto(kontoname="Girokonto", beschreibung="Bei Deutscher Bank")
    konto.save()
    
    ut = [
        UmsatzTyp(typname="Einzahlung", beschreibung="Einzahlung Mitgliedsbeitrag"),
        UmsatzTyp(typname="Rechnung", beschreibung="Begleichung von Rechnung"),
        ]
    
    umsatz = Umsatz(konto=konto,typ=ut[1],text="Jahrebeitrag DJH", centWert=12203,rechnung="blub",geschaeftspartner="DJH")
    umsatz.save()
    
    mkbt = [
        MitgliedskontoBuchungstyp(typname="Einzahlung"),
        MitgliedskontoBuchungstyp(typname="Gutschrift"),
        MitgliedskontoBuchungstyp(typname="Mitgliedsbeitrag 2017"),
        ]


    mkb = [
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[1],centWert=-10),
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[0],centWert=10),
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[2],centWert=-10),
        ]

    User.objects.bulk_create(testusers)
    Mitglied.objects.bulk_create(testmitglieder)
    BenutzerMitglied.objects.bulk_create(bm)
    UmsatzTyp.objects.bulk_create(ut)
    MitgliedskontoBuchungstyp.objects.bulk_create(mkbt)
    MitgliedskontoBuchung.objects.bulk_create(mkb)
