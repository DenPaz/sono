import zoneinfo

from django.utils import timezone
from django.utils import translation


class UserLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile and profile.language != translation.get_language():
                translation.activate(profile.language)
        return self.get_response(request)


class UserTimezoneMiddleware:
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
