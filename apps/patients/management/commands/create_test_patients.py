# ruff: noqa: S311
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.patients.models import Patient
from apps.patients.tests.factories import PatientFactory
from apps.users.models import Parent
from apps.users.models import Specialist


class Command(BaseCommand):
    help = "Create test patients."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing patients before creating new ones.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        reset = options["reset"]

        if reset:
            self.stdout.write(self.style.WARNING("Resetting patients..."))
            Patient.objects.all().delete()

        parents = list(Parent.objects.all())
        specialists = list(Specialist.objects.all())

        patients = [
            PatientFactory.build(
                parent=random.choice(parents),
                specialist=random.choice(specialists) if specialists else None,
            )
            for _ in range(count)
        ]

        Patient.objects.bulk_create(patients)

        self.stdout.write(self.style.SUCCESS(f"Created {count} patients."))
