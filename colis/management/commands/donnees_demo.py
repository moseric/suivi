from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from colis.models import Agence, Colis, Evenement, Statut, Tarif


class Command(BaseCommand):
    help = "Crée des données d'exemple : tarifs, agences et un colis."

    def handle(self, *args, **options):
        Tarif.objects.get_or_create(service="standard", defaults={"prix_base": Decimal("2000"), "prix_par_kg": Decimal("500"), "delai_jours": 3})
        Tarif.objects.get_or_create(service="express", defaults={"prix_base": Decimal("4000"), "prix_par_kg": Decimal("900"), "delai_jours": 1})
        Agence.objects.get_or_create(nom="Agence centrale", ville="Ville A", defaults={"adresse": "[Adresse]", "telephone": "[Téléphone]"})
        colis = Colis.objects.create(
            expediteur_nom="Expéditeur Exemple", destinataire_nom="Destinataire Exemple",
            ville_depart="Ville A", ville_arrivee="Ville B", poids_kg=3.5,
        )
        maintenant = timezone.now()
        Evenement.objects.create(colis=colis, statut=Statut.PRIS_EN_CHARGE, lieu="Agence de Ville A",
                                 description="Colis pris en charge", date_heure=maintenant - timedelta(hours=20))
        Evenement.objects.create(colis=colis, statut=Statut.EN_TRANSIT, lieu="Centre de tri de Ville A",
                                 description="Départ de l'agence de tri", date_heure=maintenant - timedelta(hours=6))
        self.stdout.write(self.style.SUCCESS(f"Colis de démonstration créé : {colis.numero_suivi}"))
