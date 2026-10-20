import secrets
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Statut(models.TextChoices):
    ENREGISTRE = "enregistre", "Enregistré"
    PRIS_EN_CHARGE = "pris_en_charge", "Pris en charge"
    EN_TRANSIT = "en_transit", "En transit"
    EN_LIVRAISON = "en_livraison", "En livraison"
    LIVRE = "livre", "Livré"


class Agence(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200, blank=True)
    telephone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["ville", "nom"]

    def __str__(self):
        return f"{self.nom} ({self.ville})"


class Colis(models.Model):
    SERVICES = [("standard", "Standard"), ("express", "Express")]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="colis", verbose_name="client",
    )
    numero_suivi = models.CharField("numéro de suivi", max_length=20, unique=True, editable=False)
    expediteur_nom = models.CharField("expéditeur", max_length=120)
    destinataire_nom = models.CharField("destinataire", max_length=120)
    destinataire_telephone = models.CharField("téléphone du destinataire", max_length=30, blank=True)
    ville_depart = models.CharField("ville de départ", max_length=100)
    ville_arrivee = models.CharField("ville d'arrivée", max_length=100)
    poids_kg = models.DecimalField("poids (kg)", max_digits=7, decimal_places=2)
    service = models.CharField(max_length=10, choices=SERVICES, default="standard")
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ENREGISTRE, editable=False)
    date_livraison_estimee = models.DateField("livraison estimée", null=True, blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "colis"

    def __str__(self):
        return self.numero_suivi

    def save(self, *args, **kwargs):
        nouveau = self._state.adding
        if not self.numero_suivi:
            while True:
                numero = f"TR-{timezone.now():%Y}-{secrets.randbelow(10**6):06d}"
                if not Colis.objects.filter(numero_suivi=numero).exists():
                    self.numero_suivi = numero
                    break
        if nouveau and not self.date_livraison_estimee:
            tarif = Tarif.objects.filter(service=self.service).first()
            if tarif:
                self.date_livraison_estimee = timezone.now().date() + timedelta(days=tarif.delai_jours)
        super().save(*args, **kwargs)
        if nouveau:
            Evenement.objects.create(
                colis=self, statut=Statut.ENREGISTRE, lieu=self.ville_depart, description="Envoi enregistré"
            )

    @property
    def destinataire_masque(self):
        return " ".join(p[0].upper() + "." for p in self.destinataire_nom.split()) or "—"

    def etapes(self):
        ordre = [s for s, _ in Statut.choices]
        idx = len(ordre) if self.statut == Statut.LIVRE else ordre.index(self.statut)
        return [
            {"label": label, "etat": "fait" if i < idx else "courant" if i == idx else "attente"}
            for i, (_, label) in enumerate(Statut.choices)
        ]


class Evenement(models.Model):
    colis = models.ForeignKey(Colis, on_delete=models.CASCADE, related_name="evenements")
    statut = models.CharField(max_length=20, choices=Statut.choices)
    lieu = models.CharField(max_length=120)
    description = models.CharField(max_length=200)
    date_heure = models.DateTimeField("date et heure", default=timezone.now)

    class Meta:
        ordering = ["-date_heure"]
        verbose_name = "événement"

    def __str__(self):
        return f"{self.colis} – {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        dernier = self.colis.evenements.first()
        if dernier and dernier.statut != self.colis.statut:
            self.colis.statut = dernier.statut
            self.colis.save(update_fields=["statut"])


class Tarif(models.Model):
    service = models.CharField(max_length=10, choices=Colis.SERVICES, unique=True)
    prix_base = models.DecimalField("prix de base", max_digits=10, decimal_places=2)
    prix_par_kg = models.DecimalField("prix par kg", max_digits=10, decimal_places=2)
    delai_jours = models.PositiveSmallIntegerField("délai indicatif (jours)", default=3)

    class Meta:
        ordering = ["prix_base"]

    def __str__(self):
        return self.get_service_display()

    def estimer(self, poids):
        return self.prix_base + self.prix_par_kg * Decimal(poids)


class Message(models.Model):
    num_colis = models.CharField(max_length=120)
    motif = models.CharField( max_length=120)
    statut = models.CharField(max_length=150, choices=Statut.choices, default=Statut.ENREGISTRE)
    contenu = models.TextField("message")
    created_at = models.DateTimeField("édité le", auto_now_add=True)
    lu = models.BooleanField("lu", default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.statut} – {self.num_colis} – {self.motif}"
