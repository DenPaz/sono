# ruff: noqa: S311
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.patients.models import Patient
from apps.patients.models import QuestionnaireResponse
from apps.patients.tests.factories import QuestionnaireResponseFactory


class Command(BaseCommand):
    help = "Create test questionnaire responses."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=2)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing responses before creating new ones.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        reset = options["reset"]

        if reset:
            self.stdout.write(
                self.style.WARNING("Resetting questionnaire responses...")
            )
            QuestionnaireResponse.objects.all().delete()

        patients = list(Patient.objects.all())

        responses = [
            QuestionnaireResponseFactory.build(patient=random.choice(patients))
            for _ in range(count * len(patients))
        ]

        QuestionnaireResponse.objects.bulk_create(responses)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(responses)} questionnaire responses "
                f"for {len(patients)} patients."
            )
        )
