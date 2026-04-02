from django.conf import settings


def allauth_settings(request):
    """Expose some django-allauth settings to the templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }
