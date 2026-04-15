from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from apps.users.models import User
from apps.users.models import UserProfile

BATCH_SIZE = 500
SHARED_PASSWORD_RAW = "12345"  # noqa: S105
SHARED_PASSWORD = make_password(SHARED_PASSWORD_RAW)


class Command(BaseCommand):
    help = "Create test users for development and testing purposes."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)
        parser.add_argument("--clean", action="store_true")

    @staticmethod
    def _ensure_debug_mode() -> None:
        if not settings.DEBUG:
            msg = "Este comando só pode ser executado em ambiente DEBUG."
            raise CommandError(msg)

    @staticmethod
    def _next_available_user_index() -> int:
        max_index = 0
        for email in User.objects.filter(email__startswith="user_").values_list(
            "email", flat=True
        ):
            local_part = email.split("@", 1)[0]
            if not local_part.startswith("user_"):
                continue
            raw_index = local_part[5:]
            if not raw_index.isdigit():
                continue
            max_index = max(max_index, int(raw_index))
        return max_index + 1

    @transaction.atomic
    def handle(self, *args, **options):
        self._ensure_debug_mode()

        count = options["count"]
        clean = options["clean"]
        if count < 1:
            msg = "O parâmetro --count precisa ser maior que zero."
            raise CommandError(msg)

        if clean:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Deleted existing test users."))

        start_index = self._next_available_user_index()
        users = [
            User(
                first_name=f"User{index}",
                last_name="Test",
                email=f"user_{index}@example.com",
                is_active=True,
                is_staff=False,
                is_superuser=False,
                password=SHARED_PASSWORD,
            )
            for index in range(start_index, start_index + count)
        ]
        User.objects.bulk_create(users, batch_size=BATCH_SIZE)

        created_users = list(
            User.objects.filter(
                email__in=[user.email for user in users],
            ).only("id")
        )
        UserProfile.objects.bulk_create(
            [UserProfile(user=user) for user in created_users],
            batch_size=BATCH_SIZE,
        )

        self.stdout.write(self.style.SUCCESS(f"Created {count} test users."))
