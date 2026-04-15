from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from apps.assessments import constants
from apps.assessments.models import Municipality
from apps.assessments.models import ProfessionalProfile
from apps.assessments.permissions import ensure_assessment_groups

User = get_user_model()

DEFAULT_PROFESSIONAL_EMAIL = "user@email.com"
DEFAULT_PROFESSIONAL_PASSWORD = "12345"  # noqa: S105
DEFAULT_PROFESSIONAL_FIRST_NAME = "Usuário"
DEFAULT_PROFESSIONAL_LAST_NAME = "Profissional"
DEFAULT_PROFESSIONAL_MUNICIPALITY_NAME = "Sao Paulo"
DEFAULT_PROFESSIONAL_MUNICIPALITY_STATE_CODE = "SP"


class Command(BaseCommand):
    help = (
        "Create or update the default non-manager "
        "professional user for local testing."
    )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            msg = "Este comando só pode ser executado em ambiente DEBUG."
            raise CommandError(msg)

        ensure_assessment_groups()

        professional_group = Group.objects.get(name=constants.ROLE_PROFESSIONAL)
        chief_admin_group = Group.objects.get(name=constants.ROLE_CHIEF_ADMIN)

        user, created = User.objects.update_or_create(
            email=DEFAULT_PROFESSIONAL_EMAIL,
            defaults={
                "first_name": DEFAULT_PROFESSIONAL_FIRST_NAME,
                "last_name": DEFAULT_PROFESSIONAL_LAST_NAME,
                "is_staff": False,
                "is_superuser": False,
                "is_active": True,
            },
        )

        user.set_password(DEFAULT_PROFESSIONAL_PASSWORD)
        user.save()

        user.groups.remove(chief_admin_group)
        user.groups.add(professional_group)

        municipality, _ = Municipality.objects.get_or_create(
            name=DEFAULT_PROFESSIONAL_MUNICIPALITY_NAME,
            state_code=DEFAULT_PROFESSIONAL_MUNICIPALITY_STATE_CODE,
            defaults={"is_active": True},
        )
        if not municipality.is_active:
            municipality.is_active = True
            municipality.save(update_fields=["is_active", "modified"])

        ProfessionalProfile.objects.update_or_create(
            user=user,
            defaults={
                "is_active": True,
                "municipality": municipality,
            },
        )

        EmailAddress.objects.update_or_create(
            user=user,
            email=user.email,
            defaults={"verified": True, "primary": True},
        )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{action} default professional user: {user.email}")
        )
