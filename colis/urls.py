from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib import admin
from .admin import MessageAdmin

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("suivi/<str:numero>/", views.suivi, name="suivi"),
    path("services/", views.services, name="services"),
    path("tarifs/", views.tarifs, name="tarifs"),
    path("agences/", views.agences, name="agences"),
    path("contact/<str:numero>/", views.contact, name="contact"),
    path("compte/inscription/", views.inscription, name="inscription"),
    path("compte/connexion/", auth_views.LoginView.as_view(), name="connexion"),
    path("compte/deconnexion/", auth_views.LogoutView.as_view(), name="deconnexion"),
    path("compte/mes-colis/", views.mes_colis, name="mes_colis"),
    path("compte/nouvel-envoi/", views.nouvel_envoi, name="nouvel_envoi"),
    path('administration/', views.admin_site, name='administration'),
]
