from django.contrib import admin
from django.utils.html import format_html

from .models import Agence, Colis, Evenement, Message, Statut, Tarif

admin.site.site_header = "Administration – Suivi de colis"
admin.site.site_title = "Suivi de colis"
admin.site.index_title = "Gestion des envois"

COULEURS = {
    Statut.ENREGISTRE: "#2B3A4E", Statut.PRIS_EN_CHARGE: "#123C73", Statut.EN_TRANSIT: "#8A2C06",
    Statut.EN_LIVRAISON: "#4F1F73", Statut.LIVRE: "#14543A",
}


class EvenementInline(admin.TabularInline):
    model = Evenement
    extra = 1


@admin.register(Colis)
class ColisAdmin(admin.ModelAdmin):
    list_display = ("numero_suivi", "destinataire_nom", "ville_depart", "ville_arrivee", "statut_colore", "date_livraison_estimee", "client")
    list_filter = ("statut", "service", "ville_arrivee")
    search_fields = ("numero_suivi", "destinataire_nom", "expediteur_nom", "client__username")
    readonly_fields = ("numero_suivi", "statut", "created_at")
    date_hierarchy = "created_at"
    list_select_related = ("client",)
    inlines = [EvenementInline]
    actions = ["marquer_livre"]

    @admin.display(description="Statut", ordering="statut")
    def statut_colore(self, obj):
        return format_html('<b style="color:{}">{}</b>', COULEURS[obj.statut], obj.get_statut_display())

    @admin.action(description="Marquer les colis sélectionnés comme livrés")
    def marquer_livre(self, request, queryset):
        for colis in queryset:
            Evenement.objects.create(colis=colis, statut=Statut.LIVRE, lieu=colis.ville_arrivee, description="Colis livré")
        self.message_user(request, f"{queryset.count()} colis marqué(s) comme livré(s).")


@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville", "adresse", "telephone")
    search_fields = ("nom", "ville")


@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ("service", "prix_base", "prix_par_kg", "delai_jours")


class MessageAdmin(admin.ModelAdmin):
    message= Message
    list_display = ("sujet", "num_colis", "motif", "created_at", "lu")
    list_filter = ("lu",)
    search_fields = ("sujet", "num_colis")
    readonly_fields = ("num_colis", "motif", "sujet", "contenu", "created_at")
    actions = ["marquer_lu"]

    def marquer_lu(self, request, queryset):
        queryset.update(lu=True)
