from typing import TYPE_CHECKING

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

from .enums import UserRole

if TYPE_CHECKING:
    from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """Check whether the site is open for registration."""
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def save_user(self, request, user, form, *, commit=True):
        """Set the default role for new users to PARENT."""
        user.role = UserRole.PARENT
        return super().save_user(request, user, form, commit=commit)
