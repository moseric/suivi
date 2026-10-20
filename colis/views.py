from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm, EnvoiForm, EstimationForm, InscriptionForm
from .models import Agence, Colis, Tarif, Message
from .admin import MessageAdmin


def accueil(request):
    numero = request.GET.get("numero", "").strip().upper()
    erreur = None
    if numero:
        if Colis.objects.filter(numero_suivi=numero).exists():
            return redirect("suivi", numero= numero )
        erreur = "Aucun colis ne correspond à ce numéro. Vérifiez-le et réessayez."
    return render(request, "colis/accueil.html", {"erreur": erreur, "numero": numero})


def suivi(request, numero):
    colis = get_object_or_404(Colis, numero_suivi=numero.upper())
    Messages = Message.objects.filter(num_colis=numero).order_by("-created_at").first()
    etape = Message.objects.filter(num_colis=numero).order_by("-created_at")
    return render(request, "colis/suivi.html", {'Messages': Messages,"colis": colis, "evenements": colis.evenements.all(), "etapes": colis.etapes()})


def services(request):
    return render(request, "colis/services.html", {"tarifs": Tarif.objects.all()})


def tarifs(request):
    form = EstimationForm(request.GET or None)
    estimation = None
    if form.is_valid():
        tarif = Tarif.objects.filter(service=form.cleaned_data["service"]).first()
        if tarif:
            estimation = {"prix": tarif.estimer(form.cleaned_data["poids"]), "delai": tarif.delai_jours}
        else:
            form.add_error(None, "Ce service n'a pas encore de tarif.")
    return render(request, "colis/tarifs.html", {"tarifs": Tarif.objects.all(), "form": form, "estimation": estimation})


def agences(request):
    return render(request, "colis/agences.html", {"agences": Agence.objects.all()})

def contact(request, numero):
    numero = numero.strip().upper()
    colis = Colis.objects.filter(numero_suivi=numero).first()

    if not colis:
        messages.error(request, "Aucun colis ne correspond à ce numéro. Vérifiez-le et réessayez.")
        return redirect("mes_colis")

    form = ContactForm(request.POST or None, initial={"num_colis": numero})

    if request.method == "POST" and form.is_valid():
        form.save()
        colis.statut = form.cleaned_data["statut"]
        colis.save()
        messages.success(request, "Votre message a été envoyé. Nous vous répondrons dans les plus brefs délais.")
        return redirect("contact", numero=numero)

    return render(request, "colis/contact.html", {"form": form, "colis": colis})


def inscription(request):
    form = InscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("mes_colis")
    return render(request, "registration/inscription.html", {"form": form})


@login_required
def mes_colis(request):
    return render(request, "colis/mes_colis.html", {"colis_list": Colis.objects.filter(client=request.user)})


@login_required
def nouvel_envoi(request):
    form = EnvoiForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        colis = form.save(commit=False)
        colis.client = request.user
        colis.save()
        messages.success(request, f"Envoi enregistré. Votre numéro de suivi est {colis.numero_suivi}.")
        return redirect("suivi", numero=colis.numero_suivi)
    return render(request, "colis/nouvel_envoi.html", {"form": form})

def page_404(request, exception):
    return render(request, "colis/404.html", status=404)

@login_required
def admin_site(request):
    colibrut = list(Colis.objects.values())   # toutes les colonnes de la table
    return render(request, "colis/admin-suivi-colis.html", {
        "colis_list": colibrut
    })