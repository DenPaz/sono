from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import IntegrityError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.assessments import constants
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import Municipality
from apps.assessments.services.edsc_scoring import EdscScoreResult
from apps.assessments.services.edsc_scoring import calculate_edsc_scores
from apps.assessments.services.edsc_scoring import normalize_edsc_answers
from apps.assessments.services.edsc_scoring import validate_edsc_answers

if TYPE_CHECKING:
    from collections.abc import Mapping


def get_default_municipality() -> Municipality:
    municipality = Municipality.objects.active().first()
    if municipality:
        return municipality
    return Municipality.objects.create(
        name=_("Não informado"),
        state_code="NI",
    )


@transaction.atomic
def get_or_create_draft_evaluation(*, user) -> AssessmentEvaluation:
    draft = (
        AssessmentEvaluation.objects.select_for_update()
        .select_related("municipality")
        .filter(
            professional=user,
            status=constants.EVALUATION_STATUS_DRAFT,
            is_active=True,
        )
        .order_by("-modified")
        .first()
    )
    if draft:
        return draft

    profile = getattr(user, "assessments_profile", None)
    municipality = (
        profile.municipality
        if profile and profile.municipality
        else get_default_municipality()
    )
    try:
        return AssessmentEvaluation.objects.create(
            professional=user,
            municipality=municipality,
            status=constants.EVALUATION_STATUS_DRAFT,
        )
    except IntegrityError as exc:
        draft = (
            AssessmentEvaluation.objects.select_related("municipality")
            .filter(
                professional=user,
                status=constants.EVALUATION_STATUS_DRAFT,
                is_active=True,
            )
            .order_by("-modified")
            .first()
        )
        if draft:
            return draft
        msg = (
            "Não foi possível recuperar o rascunho da avaliação "
            "após conflito de concorrência."
        )
        raise RuntimeError(msg) from exc


def is_evaluation_visible_to_user(
    *,
    evaluation: AssessmentEvaluation,
    user,
    can_view_all_assessments: bool,
) -> bool:
    if user.is_superuser or can_view_all_assessments:
        return True
    return evaluation.professional_id == user.id


@transaction.atomic
def persist_identification_step(
    *,
    evaluation: AssessmentEvaluation,
    cleaned_data: Mapping[str, object],
) -> None:
    evaluation.set_child_name(str(cleaned_data["child_name"]))
    evaluation.child_age = cleaned_data.get("child_age")
    evaluation.municipality = cleaned_data["municipality"]
    evaluation.current_step = 1
    evaluation.save(
        update_fields=[
            "child_name",
            "child_name_encrypted",
            "child_name_blind_index",
            "child_age",
            "municipality",
            "current_step",
            "modified",
        ]
    )


@transaction.atomic
def persist_questionnaire_step_answers(
    *,
    evaluation: AssessmentEvaluation,
    cleaned_answers: Mapping[int, int],
    next_step: int,
) -> None:
    normalized_answers = normalize_edsc_answers(evaluation.answers or {})
    normalized_answers.update(cleaned_answers)

    evaluation.answers = {
        str(item_index): score for item_index, score in normalized_answers.items()
    }
    evaluation.current_step = next_step
    evaluation.save(update_fields=["answers", "current_step", "modified"])


def get_step_answers(
    *,
    evaluation: AssessmentEvaluation,
    item_indexes: tuple[int, ...],
) -> dict[int, int]:
    normalized_answers = normalize_edsc_answers(evaluation.answers or {})
    return {
        item_index: normalized_answers[item_index]
        for item_index in item_indexes
        if item_index in normalized_answers
    }


def get_progress_percent(*, current_step: int) -> int:
    base = max(current_step + 1, 1)
    return int((base / constants.WIZARD_TOTAL_STEPS) * 100)


@transaction.atomic
def finalize_questionnaire(*, evaluation: AssessmentEvaluation) -> EdscScoreResult:
    normalized_answers = normalize_edsc_answers(evaluation.answers or {})
    validate_edsc_answers(answers=normalized_answers)

    result = calculate_edsc_scores(answers=normalized_answers)
    subscale_payload = {
        key: {
            "label": subscale.label,
            "item_indexes": list(subscale.item_indexes),
            "score": subscale.score,
            "acceptable_max": subscale.acceptable_max,
            "is_alert": subscale.is_alert,
        }
        for key, subscale in result.subscales.items()
    }

    evaluation.mark_completed(
        total_score=result.total_score,
        alert_count=result.alert_count,
        risk_level=result.risk_level,
        subscale_scores=subscale_payload,
    )
    evaluation.save()
    return result
