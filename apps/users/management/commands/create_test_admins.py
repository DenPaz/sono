from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand

from apps.users.models import Admin

users = [
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
    help = "Create or update test admin users."

    def handle(self, *args, **options):
        for user_data in users:
            user, created = Admin.objects.update_or_create(
                email=user_data["email"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
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
            self.stdout.write(style(f"{action} admin user: {user}"))
