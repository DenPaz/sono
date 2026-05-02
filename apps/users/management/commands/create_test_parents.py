from allauth.account.models import EmailAddress
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.enums import UserRole
from apps.users.models import Parent
from apps.users.models import ParentProfile
from apps.users.tests.factories import ParentFactory
from apps.users.tests.factories import ParentProfileFactory

SHARED_PASSWORD = make_password("12345")


class Command(BaseCommand):
    help = "Create test parent users."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing parents before creating new ones.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        reset = options["reset"]

        if reset:
            self.stdout.write(self.style.WARNING("Resetting parents..."))
            Parent.objects.all().delete()

        parents = ParentFactory.build_batch(
            count,
            password=SHARED_PASSWORD,
            role=UserRole.PARENT,
            is_staff=False,
            is_superuser=False,
        )

        created = Parent.objects.bulk_create(parents)

        ParentProfile.objects.bulk_create(
            [ParentProfileFactory.build(user=parent) for parent in created]
        )

        group = Group.objects.get(name=UserRole.PARENT)
        UserGroup = Parent.groups.through  # noqa: N806
        UserGroup.objects.bulk_create(
            [UserGroup(user=parent, group=group) for parent in created]
        )

        EmailAddress.objects.bulk_create(
            [
                EmailAddress(
                    user=parent,
                    email=parent.email,
                    verified=True,
                    primary=True,
                )
                for parent in created
            ]
        )

        self.stdout.write(self.style.SUCCESS(f"Created {count} parents."))
