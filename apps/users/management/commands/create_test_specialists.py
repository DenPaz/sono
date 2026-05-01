from allauth.account.models import EmailAddress
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.enums import UserRole
from apps.users.models import Specialist
from apps.users.models import SpecialistProfile
from apps.users.tests.factories import SpecialistFactory

SHARED_PASSWORD = make_password("12345")


class Command(BaseCommand):
    help = "Create test specialist users."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing specialists before creating new ones.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        reset = options["reset"]

        if reset:
            self.stdout.write(self.style.WARNING("Resetting specialists..."))
            Specialist.objects.all().delete()

        specialists = SpecialistFactory.build_batch(
            count,
            password=SHARED_PASSWORD,
            role=UserRole.SPECIALIST,
            is_staff=False,
            is_superuser=False,
        )

        created = Specialist.objects.bulk_create(specialists)

        SpecialistProfile.objects.bulk_create(
            [SpecialistProfile(user=specialist) for specialist in created]
        )

        group = Group.objects.get(name=UserRole.SPECIALIST)
        UserGroup = Specialist.groups.through  # noqa: N806
        UserGroup.objects.bulk_create(
            [UserGroup(user=specialist, group=group) for specialist in created]
        )

        EmailAddress.objects.bulk_create(
            [
                EmailAddress(
                    user=specialist,
                    email=specialist.email,
                    verified=True,
                    primary=True,
                )
                for specialist in created
            ]
        )

        self.stdout.write(self.style.SUCCESS(f"Created {count} specialists."))
