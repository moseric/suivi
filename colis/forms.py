from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Colis, Message


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(label="Adresse e-mail")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")


class EnvoiForm(forms.ModelForm):
    class Meta:
        model = Colis
        fields = ["expediteur_nom", "destinataire_nom", "destinataire_telephone",
                  "ville_depart", "ville_arrivee", "poids_kg", "service"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["num_colis", "motif", "statut", "contenu"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["num_colis"].widget.attrs["readonly"] = True

class EstimationForm(forms.Form):
    poids = forms.DecimalField(label="Poids (kg)", min_value=0.1, max_digits=7, decimal_places=2)
    service = forms.ChoiceField(label="Service", choices=Colis.SERVICES)
