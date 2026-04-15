from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.users.models import User
from apps.users.models import UserProfile

pytestmark = pytest.mark.django_db

EXPECTED_COUNT = 5


def test_create_test_superusers_requires_debug_mode():
    with override_settings(DEBUG=False), pytest.raises(CommandError):
        call_command("create_test_superusers")


def test_create_test_users_requires_debug_mode():
    with override_settings(DEBUG=False), pytest.raises(CommandError):
        call_command("create_test_users", count=2, clean=True)


def test_create_test_users_creates_users_with_profiles_and_shared_password():
    with override_settings(DEBUG=True):
        call_command("create_test_users", count=EXPECTED_COUNT, clean=True)

    users = list(User.objects.filter(is_superuser=False).order_by("email"))
    assert len(users) == EXPECTED_COUNT

    for user in users:
        assert user.check_password("12345") is True

    assert UserProfile.objects.filter(user__in=users).count() == EXPECTED_COUNT
