from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.assessments import constants
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import Municipality
from apps.assessments.models import ProfessionalProfile
from apps.assessments.permissions import ensure_assessment_groups
from apps.assessments.services.edsc_scoring import calculate_edsc_scores

User = get_user_model()

MUNICIPALITIES = [
    ("Sao Paulo", "SP"),
    ("Campinas", "SP"),
    ("Santos", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Niteroi", "RJ"),
    ("Belo Horizonte", "MG"),
    ("Contagem", "MG"),
    ("Curitiba", "PR"),
    ("Londrina", "PR"),
    ("Florianopolis", "SC"),
]

CHILD_NAMES = [
    "Ana",
    "Pedro",
    "Lucas",
    "Sofia",
    "Marina",
    "Joao",
    "Carlos",
    "Helena",
    "Joaquim",
    "Beatriz",
    "Gabriela",
    "Davi",
    "Livia",
    "Enzo",
    "Rafaela",
]

DEFAULT_PROFESSIONAL_EMAIL = "user@email.com"
DEFAULT_PROFESSIONAL_MUNICIPALITY_NAME = "Sao Paulo"
DEFAULT_PROFESSIONAL_MUNICIPALITY_STATE_CODE = "SP"


class Command(BaseCommand):
    help = "Populate assessments domain with fake but coherent data for dashboards and questionnaires."

    def add_arguments(self, parser):
        parser.add_argument("--evaluations", type=int, default=220)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--clean", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        ensure_assessment_groups()

        if options["clean"]:
            AssessmentEvaluation.objects.all().delete()
            ProfessionalProfile.objects.all().delete()
            Municipality.objects.all().delete()

        municipalities = self._ensure_municipalities()
        admins = self._assign_roles_and_profiles(municipalities=municipalities)
        self._create_evaluations(
            total=options["evaluations"],
            municipalities=municipalities,
            admin_users=admins,
        )

        self.stdout.write(
            self.style.SUCCESS("Assessments fake data seeded successfully.")
        )

    def _ensure_municipalities(self) -> list[Municipality]:
        rows = []
        for name, state_code in MUNICIPALITIES:
            municipality, _ = Municipality.objects.update_or_create(
                name=name,
                state_code=state_code,
                defaults={"is_active": True},
            )
            rows.append(municipality)
        return rows

    def _assign_roles_and_profiles(
        self, *, municipalities: list[Municipality]
    ) -> list:
        professional_group = Group.objects.get(name=constants.ROLE_PROFESSIONAL)
        admin_group = Group.objects.get(name=constants.ROLE_CHIEF_ADMIN)

        active_users = list(User.objects.filter(is_active=True).order_by("date_joined"))
        if not active_users:
            msg = "No users found. Run create_test_users first."
            raise RuntimeError(msg)

        superusers = [user for user in active_users if user.is_superuser]
        for user in superusers:
            user.groups.add(admin_group)

        professionals = [user for user in active_users if not user.is_superuser]
        selected_professionals = list(professionals[:60])
        default_professional = next(
            (
                user
                for user in professionals
                if user.email.casefold() == DEFAULT_PROFESSIONAL_EMAIL.casefold()
            ),
            None,
        )
        if (
            default_professional is not None
            and default_professional not in selected_professionals
        ):
            selected_professionals.append(default_professional)

        sao_paulo_municipality = next(
            (
                municipality
                for municipality in municipalities
                if municipality.name == DEFAULT_PROFESSIONAL_MUNICIPALITY_NAME
                and municipality.state_code
                == DEFAULT_PROFESSIONAL_MUNICIPALITY_STATE_CODE
            ),
            None,
        )

        for index, user in enumerate(selected_professionals, start=1):
            assigned_municipality = random.choice(municipalities)
            if (
                user.email.casefold() == DEFAULT_PROFESSIONAL_EMAIL.casefold()
                and sao_paulo_municipality is not None
            ):
                assigned_municipality = sao_paulo_municipality

            user.groups.add(professional_group)
            ProfessionalProfile.objects.update_or_create(
                user=user,
                defaults={
                    "municipality": assigned_municipality,
                    "registration_code": f"REG-{index:04d}",
                    "is_active": True,
                },
            )

        return superusers

    def _create_evaluations(
        self, *, total: int, municipalities: list[Municipality], admin_users: list
    ) -> None:
        professionals = list(
            User.objects.filter(
                groups__name=constants.ROLE_PROFESSIONAL,
                is_active=True,
            )
            .distinct()
            .select_related("assessments_profile")
        )
        if not professionals:
            msg = "No professional users were assigned."
            raise RuntimeError(msg)

        statuses = [
            constants.EVALUATION_STATUS_DRAFT,
            constants.EVALUATION_STATUS_COMPLETED,
            constants.EVALUATION_STATUS_REVIEWED,
        ]
        weights = [20, 60, 20]

        for evaluation_index in range(total):
            professional = random.choice(professionals)
            municipality = getattr(professional, "assessments_profile", None)
            municipality = (
                municipality.municipality
                if municipality and municipality.municipality
                else random.choice(municipalities)
            )
            child_name = self._build_unique_child_name(
                evaluation_index=evaluation_index
            )
            child_age = random.randint(3, 12)
            status = random.choices(statuses, weights=weights, k=1)[0]
            started_days_ago = random.randint(0, 240)
            base_date = timezone.now() - timedelta(days=started_days_ago)

            full_answers = {
                index: random.randint(
                    constants.EDSC_MIN_ITEM_VALUE, constants.EDSC_MAX_ITEM_VALUE
                )
                for index in range(1, constants.EDSC_ITEMS_COUNT + 1)
            }

            evaluation = AssessmentEvaluation(
                professional=professional,
                municipality=municipality,
                child_age=child_age,
                status=status,
                is_active=True,
            )
            evaluation.set_child_name(child_name)

            if status == constants.EVALUATION_STATUS_DRAFT:
                answered_until = random.randint(3, 20)
                partial_answers = {
                    str(index): full_answers[index]
                    for index in range(1, answered_until + 1)
                }
                evaluation.answers = partial_answers
                evaluation.current_step = random.randint(1, 4)
                evaluation.created = base_date
                evaluation.modified = base_date + timedelta(hours=random.randint(1, 72))
                evaluation.save()
                continue

            score_result = calculate_edsc_scores(answers=full_answers)
            subscale_payload = {
                key: {
                    "label": subscale.label,
                    "item_indexes": list(subscale.item_indexes),
                    "score": subscale.score,
                    "acceptable_max": subscale.acceptable_max,
                    "is_alert": subscale.is_alert,
                }
                for key, subscale in score_result.subscales.items()
            }

            evaluation.answers = {
                str(index): value for index, value in full_answers.items()
            }
            evaluation.current_step = 4
            evaluation.total_score = score_result.total_score
            evaluation.alert_count = score_result.alert_count
            evaluation.risk_level = score_result.risk_level
            evaluation.subscale_scores = subscale_payload
            evaluation.completed_at = base_date + timedelta(hours=random.randint(2, 48))
            evaluation.created = base_date
            evaluation.modified = evaluation.completed_at

            if status == constants.EVALUATION_STATUS_REVIEWED and admin_users:
                evaluation.reviewed_by = random.choice(admin_users)
                evaluation.reviewed_at = evaluation.completed_at + timedelta(
                    hours=random.randint(2, 24)
                )

            evaluation.save()

    @staticmethod
    def _build_unique_child_name(*, evaluation_index: int) -> str:
        # Keep deterministic and unique child references in seeded data.
        first_name = CHILD_NAMES[evaluation_index % len(CHILD_NAMES)]
        second_name = CHILD_NAMES[(evaluation_index // len(CHILD_NAMES)) % len(CHILD_NAMES)]
        suffix = f"{evaluation_index + 1:03d}"
        return f"{first_name} {second_name} {suffix}"
