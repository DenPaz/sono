from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.assessments import constants
from apps.assessments.models import ProfessionalProfile
from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_create_default_professional_user_requires_debug_mode():
    with override_settings(DEBUG=False), pytest.raises(CommandError):
        call_command("create_default_professional_user")


def test_create_default_professional_user_creates_active_professional_in_debug_mode():
    with override_settings(DEBUG=True):
        call_command("create_default_professional_user")

    user = User.objects.get(email="user@email.com")
    profile = ProfessionalProfile.objects.get(user=user)

    assert user.is_active is True
    assert profile.is_active is True
    assert user.groups.filter(name=constants.ROLE_PROFESSIONAL).exists()
    assert not user.groups.filter(name=constants.ROLE_CHIEF_ADMIN).exists()
