from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.models import User
from apps.users.models import UserProfile
from apps.users.tests.factories import UserFactory

SHARED_PASSWORD = make_password("12345")


class Command(BaseCommand):
    help = "Create test users for development and testing purposes."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)
        parser.add_argument("--clean", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        clean = options["clean"]

        if clean:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Deleted existing test users."))

        users = UserFactory.build_batch(count)
        for user in users:
            user.password = SHARED_PASSWORD
        User.objects.bulk_create(users)
        UserProfile.objects.bulk_create([UserProfile(user=user) for user in users])
        self.stdout.write(self.style.SUCCESS(f"Created {count} test users."))
