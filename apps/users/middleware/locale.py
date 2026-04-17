import zoneinfo

from django.conf import settings
from django.utils import timezone
from django.utils import translation


class UserLocaleMiddleware:
    """Middleware to set the user's preferred language."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = getattr(user, "profile", None)
            if (
                profile
                and profile.language
                and profile.language != translation.get_language()
            ):
                translation.activate(profile.language)

        response = self.get_response(request)

        language_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if not language_cookie or language_cookie != translation.get_language():
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME, translation.get_language()
            )
        return response


class UserTimezoneMiddleware:
    """Middleware to set the user's preferred timezone."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile and profile.timezone:
                try:
                    timezone.activate(zoneinfo.ZoneInfo(profile.timezone))
                except zoneinfo.ZoneInfoNotFoundError:
                    timezone.deactivate()
            else:
                timezone.deactivate()
        return self.get_response(request)
