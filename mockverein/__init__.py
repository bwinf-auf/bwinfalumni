from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp, Lastschriftmandat
from umsaetze.models import Umsatz, UmsatzTyp, Konto



def erstelle_mockdaten():
    testuser1 = User.objects.create_user('test', 'test@example.com', 'test', is_staff=True)
    testuser2 = User.objects.create_user('max', 'max@example.com', 'max', is_staff=True)
    testuser3 = User.objects.create_user('willi', 'willi@example.com', 'willi', is_staff=True)
    testuser4 = User.objects.create_user('williadmin', 'willi@example.com', 'willi', is_staff=True)
    testuser5 = User.objects.create_user('nico', 'nico@example.com', 'nico', is_staff=True)
    testuser1.save()
    testuser2.save()
    testuser3.save()
    testuser4.save()
    testuser5.save()
    
    testmitglied1 = Mitglied(mitgliedsnummer=99927, vorname="Test", nachname="Testofsky", strasse="Str", plz="12343", stadt="B.", telefon="0", email="test@example.com") 
    testmitglied2 = Mitglied(mitgliedsnummer=99928, vorname="Max", nachname="Mustermann", strasse="Str", plz="12343", stadt="B.", telefon="0", email="max@example.com")
    testmitglied3 = Mitglied(mitgliedsnummer=99929, vorname="Willi", nachname="Vanilly", strasse="Str", plz="12343", stadt="B.", telefon="0", email="willi@example.com")
    testmitglied4 = Mitglied(mitgliedsnummer=99930, vorname="Lena", nachname="Lane", strasse="Str", plz="12343", stadt="B.", telefon="0", email="lena@example.com")
    testmitglied1.save()
    testmitglied2.save()
    testmitglied3.save()
    testmitglied4.save()
    
    bm1 = BenutzerMitglied(benutzer=testuser1, mitglied=testmitglied1)
    bm2 = BenutzerMitglied(benutzer=testuser2, mitglied=testmitglied2)
    bm3 = BenutzerMitglied(benutzer=testuser3, mitglied=testmitglied3)
    bm4 = BenutzerMitglied(benutzer=testuser4, mitglied=testmitglied3)
    bm1.save()
    bm2.save()
    bm3.save()
    bm4.save()
    
    konto = Konto(kontoname="Girokonto", beschreibung="Bei Deutscher Bank")
    konto.save()
    
    ut1 = UmsatzTyp(typname="Einzahlung", beschreibung="Einzahlung Mitgliedsbeitrag")
    ut2 = UmsatzTyp(typname="Rechnung", beschreibung="Begleichung von Rechnung")
    ut1.save()
    ut2.save()
    
    umsatz = Umsatz(konto=konto,typ=ut2,text="Jahrebeitrag DJH", centWert=12203,rechnung="blub",geschaeftspartner="DJH")
    umsatz.save()
    
    mkbt1 = MitgliedskontoBuchungstyp(typname="Einzahlung")
    mkbt2 = MitgliedskontoBuchungstyp(typname="Gutschrift")
    mkbt3 = MitgliedskontoBuchungstyp(typname="Mitgliedsbeitrag 2017")
    mkbt1.save()
    mkbt2.save()
    mkbt3.save()

    mkb1 = MitgliedskontoBuchung(mitglied=testmitglied2,typ=mkbt2,centWert=-10)
    mkb2 = MitgliedskontoBuchung(mitglied=testmitglied2,typ=mkbt1,centWert=10)
    mkb3 = MitgliedskontoBuchung(mitglied=testmitglied2,typ=mkbt3,centWert=-10)
    mkb1.save()
    mkb2.save()
    mkb3.save()
    
