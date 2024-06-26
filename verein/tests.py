from django.test import TestCase

from .models import Verein
from django.urls import reverse

from datetime import date

def generate_id(size=12):
    import string
    import random
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(size))

def generate_member(mitgliedsnummer=1):
    from django.contrib.auth.models import User
    from mitglieder.models import Mitglied
    from benutzer.models import BenutzerMitglied

    mitglied = Mitglied.objects.create(mitgliedsnummer=mitgliedsnummer)
    user = User.objects.create(username=generate_id())
    bm = BenutzerMitglied.objects.create(benutzer=user, mitglied=mitglied)

    return (user, mitglied)

def generate_vorstand(mitgliedsnummer=2):
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import User
    from mitglieder.models import Mitglied
    from benutzer.models import BenutzerMitglied

    mitglied = Mitglied.objects.create(mitgliedsnummer=mitgliedsnummer)
    user = User.objects.create(is_staff=True, username=generate_id())
    bm = BenutzerMitglied.objects.create(benutzer=user, mitglied=mitglied)

    vorstand = Group.objects.create(name='vorstand')
    vorstand.user_set.add(user)

    return (user, mitglied)

def generate_admin():
    from django.contrib.auth.models import User
    from mitglieder.models import Mitglied
    from benutzer.models import BenutzerMitglied

    user = User.objects.create(username=generate_id(), is_staff=True, is_superuser=True)

    return user


class IndexAccessTests(TestCase):
    def test_not_logged_in(self):
        response = self.client.get(reverse("verein:index"))
        self.assertEqual(302, response.status_code)

    def test_logged_in_member(self):
        (user, _) = generate_member()
        self.client.force_login(user)

        response = self.client.get(reverse("verein:index"))
        self.assertEqual(302, response.status_code)

    def test_logged_in_vorstand(self):
        (user, _) = generate_vorstand()
        self.client.force_login(user)

        response = self.client.get(reverse("verein:index"))
        self.assertEqual(200, response.status_code)

    def test_logged_in_admin(self):
        user = generate_admin()
        self.client.force_login(user)

        response = self.client.get(reverse("verein:index"))
        self.assertEqual(200, response.status_code)


class IndexPostAccessTests(TestCase):
    def test_not_logged_in(self):
        beschluss_before = Verein.objects.all()[0]

        response = self.client.post(reverse("verein:index"), {'beschlussfassung':'1.1.2000', 'mitgliedsbeitrag_cent':'1200'})
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, len(Verein.objects.all()))
        self.assertEqual(beschluss_before, Verein.objects.all()[0])

    def test_logged_in_member(self):
        (user, _) = generate_member()
        self.client.force_login(user)

        beschluss_before = Verein.objects.all()[0]

        response = self.client.post(reverse("verein:index"), {'beschlussfassung':'1.1.2000', 'mitgliedsbeitrag_cent':'1200'})
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, len(Verein.objects.all()))
        self.assertEqual(beschluss_before, Verein.objects.all()[0])

    def test_logged_in_vorstand(self):
        (user, _) = generate_vorstand()
        self.client.force_login(user)

        beschluss_before = Verein.objects.all()[0]

        response = self.client.post(reverse("verein:index"), {'beschlussfassung':'1.1.2000', 'mitgliedsbeitrag_cent':'1200'})
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, len(Verein.objects.all()))
        self.assertEqual(beschluss_before, Verein.objects.all()[0])
        self.assertEqual(date(2000, 1, 1), Verein.objects.all()[1].beschlussfassung)
        self.assertEqual(1200, Verein.objects.all()[1].mitgliedsbeitrag_cent)

    def test_logged_in_admin(self):
        user = generate_admin()
        self.client.force_login(user)

        beschluss_before = Verein.objects.all()[0]

        response = self.client.post(reverse("verein:index"), {'beschlussfassung':'1.1.2000', 'mitgliedsbeitrag_cent':'1200'})
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, len(Verein.objects.all()))
        self.assertEqual(beschluss_before, Verein.objects.all()[0])
        self.assertEqual(date(2000, 1, 1), Verein.objects.all()[1].beschlussfassung)
        self.assertEqual(1200, Verein.objects.all()[1].mitgliedsbeitrag_cent)


class UpdateMitgliedsbeitragTests(TestCase):
    def test_logged_in_vorstand(self):
        from mitglieder.models import Mitglied

        (_, regular1) = generate_member(10)

        (_, regular2) = generate_member(11)
        regular2.beitrag_cent = 1100
        regular2.save()

        (_, foerder1) = generate_member(12)
        foerder1.foerdermitglied = True
        foerder1.save()

        (_, foerder2) = generate_member(13)
        foerder2.foerdermitglied = True
        foerder2.beitrag_cent = 1300
        foerder2.save()

        self.assertEqual(1000, Mitglied.objects.get(mitgliedsnummer=10).beitrag_cent)
        self.assertEqual(1100, Mitglied.objects.get(mitgliedsnummer=11).beitrag_cent)
        self.assertEqual(1000, Mitglied.objects.get(mitgliedsnummer=12).beitrag_cent)
        self.assertEqual(1300, Mitglied.objects.get(mitgliedsnummer=13).beitrag_cent)

        (user, _) = generate_vorstand()
        self.client.force_login(user)

        beschluss_before = Verein.objects.all()[0]

        response = self.client.post(reverse("verein:index"), {'beschlussfassung':'1.1.2000', 'mitgliedsbeitrag_cent':'1200'})
        self.assertEqual(200, response.status_code)

        self.assertEqual(1200, Mitglied.objects.get(mitgliedsnummer=10).beitrag_cent)
        self.assertEqual(1200, Mitglied.objects.get(mitgliedsnummer=11).beitrag_cent)
        self.assertEqual(1000, Mitglied.objects.get(mitgliedsnummer=12).beitrag_cent)
        self.assertEqual(1300, Mitglied.objects.get(mitgliedsnummer=13).beitrag_cent)
