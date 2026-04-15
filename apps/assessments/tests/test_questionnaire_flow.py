from __future__ import annotations

from http import HTTPStatus

import pytest
from django.urls import reverse

from apps.assessments import constants
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import Municipality
from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

STEP_TWO = 2


def _create_municipality() -> Municipality:
    return Municipality.objects.create(name="Sao Paulo", state_code="SP")


def _create_draft_evaluation(*, user, municipality, current_step: int = 1):
    return AssessmentEvaluation.objects.create(
        professional=user,
        municipality=municipality,
        status=constants.EVALUATION_STATUS_DRAFT,
        current_step=current_step,
        is_active=True,
    )


def _build_step_payload(*, evaluation_id, step: int) -> dict[str, str]:
    payload = {
        "evaluation_id": str(evaluation_id),
        "action": "next",
    }
    payload.update(
        {
            f"q_{item_index}": "1"
            for item_index in constants.WIZARD_STEP_ITEM_INDEXES[step]
        }
    )
    return payload


def test_questionnaire_post_on_non_draft_evaluation_is_forbidden(client):
    municipality = _create_municipality()
    professional = UserFactory()
    evaluation = AssessmentEvaluation.objects.create(
        professional=professional,
        municipality=municipality,
        status=constants.EVALUATION_STATUS_COMPLETED,
        is_active=True,
    )

    client.force_login(professional)

    response = client.post(
        reverse("assessments:questionnaire_step_partial", kwargs={"step": 1}),
        data={
            "evaluation_id": str(evaluation.id),
            "action": "next",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_questionnaire_invalid_step_returns_404(client):
    municipality = _create_municipality()
    professional = UserFactory()
    evaluation = _create_draft_evaluation(
        user=professional,
        municipality=municipality,
        current_step=1,
    )

    client.force_login(professional)

    response = client.post(
        reverse("assessments:questionnaire_step_partial", kwargs={"step": 99}),
        data={
            "evaluation_id": str(evaluation.id),
            "action": "next",
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_questionnaire_next_step_persists_answers_and_advances(client):
    municipality = _create_municipality()
    professional = UserFactory()
    evaluation = _create_draft_evaluation(
        user=professional,
        municipality=municipality,
        current_step=1,
    )

    client.force_login(professional)

    response = client.post(
        reverse("assessments:questionnaire_step_partial", kwargs={"step": 1}),
        data=_build_step_payload(evaluation_id=evaluation.id, step=1),
    )

    assert response.status_code == HTTPStatus.OK

    evaluation.refresh_from_db()
    assert evaluation.current_step == STEP_TWO
    assert len(evaluation.answers) == len(constants.WIZARD_STEP_ITEM_INDEXES[1])
    for item_index in constants.WIZARD_STEP_ITEM_INDEXES[1]:
        assert evaluation.answers[str(item_index)] == 1
