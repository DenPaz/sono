from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand

from apps.users.models import User

superusers = [
    {
        "first_name": "Dennis",
        "last_name": "Paz",
        "email": "dppazlopez@gmail.com",
    },
    {
        "first_name": "Alisson",
        "last_name": "Pereira",
        "email": "alissonpef@gmail.com",
    },
]
password = "12345"  # noqa: S105


class Command(BaseCommand):
    help = "Create or update test superusers with predefined credentials."

    def handle(self, *args, **kwargs):
        for superuser in superusers:
            user, created = User.objects.update_or_create(
                email=superuser["email"],
                defaults={
                    "first_name": superuser["first_name"],
                    "last_name": superuser["last_name"],
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            user.set_password(password)
            user.save()

            EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={"verified": True, "primary": True},
            )

            action = "Created" if created else "Updated"
            style = self.style.SUCCESS if created else self.style.WARNING
            self.stdout.write(style(f"{action} superuser: {user}"))
