from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Colis, Evenement, Message, Statut, Tarif


def creer_colis(**kw):
    donnees = dict(expediteur_nom="Exp", destinataire_nom="Jean Dupont", ville_depart="A", ville_arrivee="B", poids_kg=2)
    donnees.update(kw)
    return Colis.objects.create(**donnees)


class SuiviTests(TestCase):
    def test_numero_genere_et_evenement_initial(self):
        c = creer_colis()
        self.assertRegex(c.numero_suivi, r"^TR-\d{4}-\d{6}$")
        self.assertEqual(c.evenements.count(), 1)

    def test_recherche_redirige_et_inconnu_affiche_erreur(self):
        c = creer_colis()
        r = self.client.get(reverse("accueil"), {"numero": c.numero_suivi.lower()})
        self.assertRedirects(r, reverse("suivi", args=[c.numero_suivi]))
        self.assertContains(self.client.get(reverse("accueil"), {"numero": "XX"}), "Aucun colis")

    def test_page_suivi_masque_le_destinataire(self):
        c = creer_colis()
        r = self.client.get(reverse("suivi", args=[c.numero_suivi]))
        self.assertContains(r, "J. D.")
        self.assertNotContains(r, "Jean Dupont")

    def test_evenement_met_a_jour_le_statut(self):
        c = creer_colis()
        Evenement.objects.create(colis=c, statut=Statut.EN_TRANSIT, lieu="X", description="Départ")
        c.refresh_from_db()
        self.assertEqual(c.statut, Statut.EN_TRANSIT)

    def test_suivi_inconnu_404(self):
        self.assertEqual(self.client.get("/suivi/NOPE/").status_code, 404)


class PagesTests(TestCase):
    def test_pages_publiques(self):
        for nom in ["accueil", "services", "tarifs", "agences", "contact", "connexion", "inscription"]:
            self.assertEqual(self.client.get(reverse(nom)).status_code, 200, nom)

    def test_estimation_tarif(self):
        Tarif.objects.create(service="standard", prix_base=Decimal("1000"), prix_par_kg=Decimal("200"), delai_jours=3)
        r = self.client.get(reverse("tarifs"), {"poids": "5", "service": "standard"})
        self.assertEqual(r.context["estimation"]["prix"], Decimal("2000"))

    def test_contact_enregistre_un_message(self):
        r = self.client.post(reverse("contact"), {"nom": "A", "email": "a@x.fr", "sujet": "S", "contenu": "Bonjour"})
        self.assertRedirects(r, reverse("contact"))
        self.assertEqual(Message.objects.count(), 1)

    def test_date_livraison_depuis_tarif(self):
        Tarif.objects.create(service="standard", prix_base=1, prix_par_kg=1, delai_jours=2)
        self.assertIsNotNone(creer_colis().date_livraison_estimee)


class CompteTests(TestCase):
    def test_mes_colis_demande_connexion(self):
        self.assertEqual(self.client.get(reverse("mes_colis")).status_code, 302)

    def test_connexion_redirige_vers_administration(self):
        utilisateur = get_user_model().objects.create_user(
            username="responsable",
            password="Mot-de-passe-solide-42",
        )
        response = self.client.post(
            reverse("connexion"),
            {"username": utilisateur.username, "password": "Mot-de-passe-solide-42"},
        )
        self.assertRedirects(response, reverse("administration"))

    def test_inscription_puis_envoi(self):
        r = self.client.post(reverse("inscription"), {"username": "client1", "email": "c@x.fr",
                             "password1": "Mot-de-passe-solide-42", "password2": "Mot-de-passe-solide-42"})
        self.assertRedirects(r, reverse("mes_colis"))
        r = self.client.post(reverse("nouvel_envoi"), {"expediteur_nom": "E", "destinataire_nom": "D", "destinataire_telephone": "",
                             "ville_depart": "A", "ville_arrivee": "B", "poids_kg": "1.5", "service": "standard"})
        colis = Colis.objects.get()
        self.assertEqual(colis.client.username, "client1")
        self.assertRedirects(r, reverse("suivi", args=[colis.numero_suivi]))
        self.assertContains(self.client.get(reverse("mes_colis")), colis.numero_suivi)

    def test_admin_reserve_au_staff(self):
        U = get_user_model()
        U.objects.create_user("simple", password="x-y-z-12345")
        self.client.login(username="simple", password="x-y-z-12345")
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        U.objects.create_superuser("chef", "c@x.fr", "x-y-z-12345")
        self.client.login(username="chef", password="x-y-z-12345")
        for url in ["/admin/", "/admin/colis/colis/", "/admin/colis/tarif/", "/admin/colis/message/", "/admin/colis/agence/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
