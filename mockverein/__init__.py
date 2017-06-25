from django.contrib.auth.models import User
from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp, Lastschriftmandat
from umsaetze.models import Umsatz, UmsatzTyp, Konto



def erstelle_mockdaten():
    testusers = [
        User.objects.create_user(username='test', email='test@example.com', password='test'),
        User.objects.create_user(username='max', email='max@example.com', password='max'),
        User.objects.create_user(username='willi', email='willi@example.com', password='willi'),
        User.objects.create_user(username='williadmin', email='willi@example.com', password='willi'),
        User.objects.create_user(username='nico', email='nico@example.com', password='nico'),
        ]
    
    for user in testusers:
        user.is_staff = True
    
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
        BenutzerMitglied(benutzer=testusers[3], mitglied=testmitglieder[2]),
        ]
    
    konto = Konto(kontoname="Girokonto", beschreibung="Bei Deutscher Bank")
    konto.save()
    
    ut = [
        UmsatzTyp(typname="Einzahlung", beschreibung="Einzahlung Mitgliedsbeitrag"),
        UmsatzTyp(typname="Rechnung", beschreibung="Begleichung von Rechnung"),
        ]
    
    for o in ut:
        o.save()
    
    umsaetze = [
        Umsatz(konto=konto,typ=ut[1],text="Jahrebeitrag DJH", centWert=12203,quittung="blub",geschaeftspartner="DJH"),
        ]
    
    for o in testmitglieder:
        o.save()
    
    mkbt = [
        MitgliedskontoBuchungstyp(typname="Einzahlung"),
        MitgliedskontoBuchungstyp(typname="Gutschrift"),
        MitgliedskontoBuchungstyp(typname="Mitgliedsbeitrag 2017"),
        ]
    
    for o in mkbt:
        o.save()

    mkb = [
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[1],centWert=-10),
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[0],centWert=10),
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[2],centWert=-10),
        ]

    BenutzerMitglied.objects.bulk_create(bm);
    Umsatz.objects.bulk_create(umsaetze)
    MitgliedskontoBuchung.objects.bulk_create(mkb)

    
def loesche_nutzer():
    q1 = User.objects.filter(username='test', email='test@example.com')
    q2 = User.objects.filter(username='max', email='max@example.com')
    q3 = User.objects.filter(username='willi', email='willi@example.com')
    q4 = User.objects.filter(username='williadmin', email='willi@example.com')
    q5 = User.objects.filter(username='nico', email='nico@example.com')
    
    try:
        q1.get().benutzermitglied.delete()
    except:
        pass
    try:
        q2.get().benutzermitglied.delete()
    except:
        pass
    try:
        q3.get().benutzermitglied.delete()
    except:
        pass
    try:
        q4.get().benutzermitglied.delete()
    except:
        pass
    
    
    q1.delete()
 
    try:
        q2.delete()
    except:
        pass
    try:
        q3.delete()
    except:
        pass
    try:
        q4.delete()
    except:
        pass
    try:
        q5.delete()
    except:
        pass
    
    try:
        Mitglied.objects.filter(mitgliedsnummer=99927).delete()
    except:
        pass
    try:
        Mitglied.objects.filter(mitgliedsnummer=99928).delete()
    except:
        pass
    try:
        Mitglied.objects.filter(mitgliedsnummer=99929).delete()
    except:
        pass
    try:
        Mitglied.objects.filter(mitgliedsnummer=99930).delete()
    except:
        pass
    
    
