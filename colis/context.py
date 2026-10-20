from django.conf import settings


def reglages(request):
    return {"NOM_SOCIETE": settings.NOM_SOCIETE, "DEVISE": settings.DEVISE}
