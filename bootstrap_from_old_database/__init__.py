from django.contrib.auth.models import User
from mitglieder.models import Mitglied, MitgliedskontoBuchung, MitgliedskontoBuchungstyp, Lastschriftmandat
from benutzer.models import BenutzerMitglied
from umsaetze.models import Umsatz, UmsatzTyp, Konto

from datetime import date

import psycopg2



def run():
    infostring = ""
    
    conn = psycopg2.connect(dbname="alumni_neu", user="alumni", password="alumni", host="localhost")
    cur = conn.cursor()
    
    mbuchungstyp_default = MitgliedskontoBuchungstyp(typname = "unspezifiziert")
    mbuchungstyp_default.save()
    
    # TODO: Field Type?
    # -> Ist immer 0
    cur.execute("SELECT "
                "\"Member\".\"Id\", " #0
                "\"Member\".\"Application\", "
                "\"Member\".\"Admission\", "
                "\"Member\".\"Deleted\", "
                "\"Member\".\"Firstname\", "
                "\"Member\".\"Lastname\", " #5
                "\"Member\".\"Salutation\", "
                "\"Member\".\"Birthday\", "
                "\"Member\".\"StreetAddress\", "
                "\"Member\".\"ZIP\", "
                "\"Member\".\"City\", " #10
                "\"Country\".\"Code\", "
                "\"Member\".\"Phone\", "
                "\"Member\".\"EMail\", "
                "\"Member\".\"Occupation\", "
                "\"Member\".\"TertiaryEducationCity\", " #15
                "\"Member\".\"TertiaryEducationSubject\", "
                "\"Member\".\"PhoneSL\", "
                "\"Member\".\"EMailSL\", "
                "\"Member\".\"AddressSL\", "
                "\"Member\".\"NameAndOccupationSL\", " #20
                "\"Member\".\"IsInfoSharedWithBWInf\", "
                "\"Member\".\"AdminComment\", "
                "\"Member\".\"DunningCount\", "
                "\"Member\".\"Nickname\", " 
                "\"Member\".\"Password\", " #25
                "\"Member\".\"Disabled\", "
                "\"Member\".\"LastLogin\", "
                "\"Member\".\"DirectDebit_AccountOwner\", "
                "\"Member\".\"DirectDebit_BankName\", "
                "\"Member\".\"DirectDebit_AccountNumber\", "  # 30
                "\"Member\".\"DirectDebit_BankCode\", "
                "\"Member\".\"DirectDebit_ValidFrom\", "
                "\"Member\".\"DirectDebit_ValidTo\" "
                "FROM \"Member\" "
                "JOIN \"Country\" ON \"Member\".\"Country\" = \"Country\".\"Id\" "
                "ORDER BY \"Member\".\"Id\" ;")
    member_rows = cur.fetchall()
    for member in member_rows:
        
        teileInfo = "" + ("telefon" if member[17] else "") + ""\
                    "" + (",email" if member[18] else "") + ""\
                    "" + (",adresse" if member[19] else "") + ""\
                    "" + (",beruf" if member[20] else "") + ""\
                    "" + (",vorname" if member[20] else "") + ""\
                    "" + (",nachname" if member[20] else "")
        if teileInfo[0] == ",":
            teileInfo = teileInfo[1:]
        
        mitglied = Mitglied(mitgliedsnummer = member[0],
                            antragsdatum = member[1],
                            beitrittsdatum = member[2],
                            vorname = member[4],
                            nachname = member[5],
                            anrede = member[6],
                            geburtsdatum = member[7] if member[7] else date(1970,1,1),
                            strasse = member[8],
                            plz = member[9],
                            stadt = member[10],
                            land = member[11],
                            telefon = member[12],
                            email = member[13],
                            beruf = member[14],
                            studienort = member[15],
                            studienfach = member[16],
                            teileInfoWelt = "",
                            teileInfoAlumni = teileInfo,
                            teileInfoBwinf = "email,vorname,nachname" if member[21] else "",
                            kommentar = member[22],
                            anzahlMahnungen = member[23])
        mitglied.save()
        
        infostring += "\n" + mitglied.vorname + " " + mitglied.nachname
        
        user = User(username = member[24],
                    password = "miaplaza$" + member[25],
                    is_staff = not member[26],
                    is_active = not member[26],
                    is_superuser = False,
                    last_login = member[27])
        user.save()
        
        bm = BenutzerMitglied(benutzer = user, mitglied = mitglied)
        bm.save()
        
        if member[30]:
            lsm = Lastschriftmandat(mitglied = mitglied,
                                    kontoinhaber = member[28],
                                    bankname = member[29],
                                    iban = member[30],
                                    bic = member[31],
                                    gueltigAb = member[32],
                                    gueltigBis = member[33])
            lsm.save()
            
            infostring += "+"
            
        cur.execute("SELECT "
                    "\"Amount\", " #0
                    "\"Purpose\", "
                    "\"Booking\" "
                    "FROM \"MemberPosting\" WHERE \"Member\" = %(memberid)s ORDER BY \"Id\" ;", {"memberid": member[0]})
        memberposting_rows = cur.fetchall()
        for memberposting in memberposting_rows:
            mbuchung = MitgliedskontoBuchung(mitglied = mitglied,
                                             typ = mbuchungstyp_default,
                                             centWert = memberposting[0], 
                                             kommentar = memberposting[1],
                                             buchungsDatum = memberposting[2])
            mbuchung.save()
            
            infostring += "."


    infostring += "\n\nUmsatz"
    
    # TODO: gibt es nur einen Wert in Account?
    # -> Nein: 1. Konto, 2. Bargeld für 1. VZ, 3. 2. VZ
    # -> ABER: Alle Umsätze verweisen auf 1.
    cur.execute("SELECT "
                "\"Title\", " #0
                "\"Description\" "
                "FROM \"Account\" ORDER BY \"Id\" ;")
    account_rows = cur.fetchall()
    konto_default = Konto(kontoname = account_rows[0][0], beschreibung = account_rows[0][1])
    konto_default.save()
    
    # TODO: Field Type?
    # -> Enthält 0 für Einnahmen und 1 für Ausgaben
    # -> Beträge sind aber trotzdem Vorzeichenbehaftet.
    cur.execute("SELECT "
                "\"Title\", " #0
                "\"Description\", "
                "\"Id\" "
                "FROM \"Purpose\" ORDER BY \"Id\" ;")
    purpose_rows = cur.fetchall()
    for purpose in purpose_rows:
        umsatztyp = UmsatzTyp(typname = purpose[0], beschreibung = purpose[1])
        umsatztyp.save()
        
        infostring += "\n" + umsatztyp.typname
        
        # TODO: Was ist Author wirklich?
        # -> Wer die Buchung eingetragen hat
        cur.execute("SELECT "
                    "\"Comment\", "
                    "\"Amount\", " #0
                    "\"Receipt\", "
                    "\"Author\", "
                    "\"Booking\" "
                    "FROM \"Posting\" WHERE \"Purpose\" = %(purposeid)s ORDER BY \"Id\" ;", {"purposeid": purpose[2]})
        posting_rows = cur.fetchall()
        for posting in posting_rows:
            umsatz = Umsatz(konto = konto_default,
                            typ = umsatztyp,
                            text = posting[0],
                            centWert = posting[1],
                            quittung = posting[2],
                            author = posting[3],
                            geschaeftspartner = "k. A.",
                            wertstellungsdatum = posting[4])
            umsatz.save();
            
            infostring += "."
            

