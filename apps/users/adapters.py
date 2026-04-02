from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """Check whether the site is open for registration."""
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
