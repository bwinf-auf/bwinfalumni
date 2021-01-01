from django.contrib.auth.models import User
from benutzer.models import BenutzerMitglied
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp, Lastschriftmandat
from umsaetze.models import Umsatz, UmsatzTyp, Konto
from profil.models import Sichtbarkeit



def erstelle_mockdaten():
    testusers = [
        User.objects.create_user(username='test', email='test@example.com', password='test'),
        User.objects.create_user(username='max', email='max@example.com', password='max'),
        User.objects.create_user(username='willi', email='willi@example.com', password='willi'),
        User.objects.create_user(username='williadmin', email='willi@example.com', password='willi'),
        User.objects.create_user(username='nico', email='nico@example.com', password='nico'),
        ]
    
    testmitglieder = [
        Mitglied(mitgliedsnummer=99927, vorname="Test", nachname="Testofsky", strasse="AStr", plz="37073", stadt="Berlin", telefon="00123", email="test@example.com", studienort="Bonn", studienfach="Mathe", beruf="Geiler Hecht"),
        Mitglied(mitgliedsnummer=99928, vorname="Max", nachname="Mustermann", strasse="BStr", plz="57074", stadt="Marburg", telefon="0049123", email="max@example.com", studienort="Göttingen", studienfach="Physik"),
        Mitglied(mitgliedsnummer=99929, vorname="Willi", nachname="Vanilly", strasse="CStr", plz="57074", stadt="G-Town", telefon="57213", email="willi@example.com", studienort="Aachen", studienfach="Informatik"),
        Mitglied(mitgliedsnummer=99930, vorname="Lena", nachname="Lane", strasse="DStr", plz="40822", stadt="Erlangen", telefon="1", email="lena@example.com", studienort="Greifswald", studienfach="Spirituelle Energie"),
        ]
    
    for o in testmitglieder:
        o.save()
    
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
        Umsatz(konto=konto,typ=ut[1],text="Jahrebeitrag DJH", cent_wert=12203,beleg="blub",geschaeftspartner="DJH"),
        ]
    
    mkbt = [
        MitgliedskontoBuchungstyp(typname="Einzahlung"),
        MitgliedskontoBuchungstyp(typname="Gutschrift"),
        MitgliedskontoBuchungstyp(typname="Mitgliedsbeitrag 2017"),
        ]
    
    for o in mkbt:
        o.save()

    mkb = [
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[1],cent_wert=-10),
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[0],cent_wert=10),
        MitgliedskontoBuchung(mitglied=testmitglieder[1],typ=mkbt[2],cent_wert=-10),
        ]

    sbk = [
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="vorname"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="nachname"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="studienort"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="studienfach"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="beruf"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="email"),

        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="telefon"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="adresse"),
        Sichtbarkeit(mitglied=testmitglieder[0],bereich="alumni",sache="wohnort"),
        

        Sichtbarkeit(mitglied=testmitglieder[1],bereich="alumni",sache="vorname"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="alumni",sache="nachname"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="alumni",sache="studienort"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="alumni",sache="studienfach"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="alumni",sache="beruf"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="alumni",sache="email"),

        Sichtbarkeit(mitglied=testmitglieder[1],bereich="welt",sache="vorname"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="welt",sache="nachname"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="welt",sache="studienort"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="welt",sache="studienfach"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="welt",sache="beruf"),
        Sichtbarkeit(mitglied=testmitglieder[1],bereich="welt",sache="email"),

        Sichtbarkeit(mitglied=testmitglieder[2],bereich="alumni",sache="vorname"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="alumni",sache="nachname"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="alumni",sache="studienort"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="alumni",sache="studienfach"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="alumni",sache="beruf"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="alumni",sache="email"),

        Sichtbarkeit(mitglied=testmitglieder[2],bereich="welt",sache="vorname"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="welt",sache="studienort"),
        Sichtbarkeit(mitglied=testmitglieder[2],bereich="welt",sache="email"),

        Sichtbarkeit(mitglied=testmitglieder[3],bereich="alumni",sache="vorname"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="alumni",sache="nachname"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="alumni",sache="studienort"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="alumni",sache="studienfach"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="alumni",sache="beruf"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="alumni",sache="email"),

        Sichtbarkeit(mitglied=testmitglieder[3],bereich="welt",sache="nachname"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="welt",sache="studienfach"),
        Sichtbarkeit(mitglied=testmitglieder[3],bereich="welt",sache="beruf"),
        ]

    BenutzerMitglied.objects.bulk_create(bm);
    Umsatz.objects.bulk_create(umsaetze)
    MitgliedskontoBuchung.objects.bulk_create(mkb)
    Sichtbarkeit.objects.bulk_create(sbk);

    
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
        Sichtbarkeit.objects.filter(mitglied__mitgliedsummer=99927).delete()
    except:
        pass
    try:
        Sichtbarkeit.objects.filter(mitglied__mitgliedsummer=99928).delete()
    except:
        pass
    try:
        Sichtbarkeit.objects.filter(mitglied__mitgliedsummer=99929).delete()
    except:
        pass
    try:
        Sichtbarkeit.objects.filter(mitglied__mitgliedsummer=99930).delete()
    except:
        pass

    try:
        MitgliedskontoBuchung.objects.filter(mitglied__mitgliedsummer=99927).delete()
    except:
        pass
    try:
        MitgliedskontoBuchung.objects.filter(mitglied__mitgliedsummer=99928).delete()
    except:
        pass
    try:
        MitgliedskontoBuchung.objects.filter(mitglied__mitgliedsummer=99929).delete()
    except:
        pass
    try:
        MitgliedskontoBuchung.objects.filter(mitglied__mitgliedsummer=99930).delete()
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
    
    
