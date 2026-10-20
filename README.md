# Suivi de colis – projet Django

Site de transport complet : suivi public par numéro, espace client, pages d'information et administration.

## Contenu
- **Public** : accueil avec recherche du numéro de suivi, page de suivi (progression, historique), Services, Tarifs (avec estimation du prix), Agences, Contact.
- **Espace client** : inscription, connexion, « Mes colis », demande d'expédition (le numéro de suivi est créé automatiquement).
- **Administration** (`/admin/`) : colis (avec événements du trajet), agences, tarifs, messages de contact, utilisateurs. Action « marquer comme livrés ».
- **Tests** : `python manage.py test` (12 tests).

## Lancer en local
```
cd suivi_transport
python3 -m venv venv
source venv/bin/activate          (Windows : venv\Scripts\activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py donnees_demo     (facultatif : tarifs, agence et colis d'exemple)
python manage.py runserver
```
Site : http://127.0.0.1:8000/ · Administration : http://127.0.0.1:8000/admin/

## Utilisation de l'administration
1. **Tarifs** : créez un tarif « Standard » et un « Express » (prix de base, prix par kg, délai). Ils alimentent les pages Services et Tarifs et la date de livraison estimée.
2. **Colis** > Ajouter (ou par un client depuis le site) : à chaque étape, ajoutez un **événement** dans la fiche du colis. Le statut suit le dernier événement.
3. **Agences** : saisissez vos points de dépôt, ils apparaissent sur la page Agences.
4. **Messages** : les messages du formulaire de contact arrivent ici.

## Réglages (variables d'environnement)
| Variable | Rôle | Défaut |
|---|---|---|
| `DJANGO_DEBUG` | `0` en ligne | `1` |
| `DJANGO_SECRET_KEY` | clé secrète | clé de développement |
| `DJANGO_ALLOWED_HOSTS` | domaines autorisés, séparés par des virgules | `localhost,127.0.0.1` |
| `DJANGO_NOM_SOCIETE` | nom affiché sur le site | `[Votre société]` |
| `DJANGO_DEVISE` | devise des prix | `FCFA` |

Le fuseau horaire se règle avec `TIME_ZONE` dans `config/settings.py`.

## Mise en ligne (PythonAnywhere)
Dans le fichier WSGI, avant `get_wsgi_application()` :
```python
os.environ['DJANGO_DEBUG'] = '0'
os.environ['DJANGO_SECRET_KEY'] = 'une-longue-cle-secrete'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'votre-pseudo.pythonanywhere.com'
os.environ['DJANGO_NOM_SOCIETE'] = 'Ma Société'
```
Puis `python manage.py migrate`, `createsuperuser`, `collectstatic`, et dans l'onglet Web : fichiers statiques `/static/` → `.../staticfiles`.
