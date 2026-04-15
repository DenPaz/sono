from __future__ import annotations

from http import HTTPStatus

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

from apps.assessments import constants
from apps.assessments.forms.settings import PROFESSIONAL_ACTION_REVOKE_ACCESS
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import Municipality
from apps.assessments.models import ProfessionalProfile
from apps.assessments.permissions import ensure_assessment_groups
from apps.assessments.services.questionnaire_workflow import (
    get_or_create_draft_evaluation,
)
from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def _create_municipality() -> Municipality:
    return Municipality.objects.create(name="Sao Paulo", state_code="SP")


def test_active_draft_unique_constraint_per_professional():
    municipality = _create_municipality()
    professional = UserFactory()

    AssessmentEvaluation.objects.create(
        professional=professional,
        municipality=municipality,
        status=constants.EVALUATION_STATUS_DRAFT,
        is_active=True,
    )

    with pytest.raises(IntegrityError):
        AssessmentEvaluation.objects.create(
            professional=professional,
            municipality=municipality,
            status=constants.EVALUATION_STATUS_DRAFT,
            is_active=True,
        )


def test_get_or_create_draft_reuses_existing_active_draft():
    municipality = _create_municipality()
    professional = UserFactory()
    draft = AssessmentEvaluation.objects.create(
        professional=professional,
        municipality=municipality,
        status=constants.EVALUATION_STATUS_DRAFT,
        is_active=True,
        current_step=2,
    )

    resolved = get_or_create_draft_evaluation(user=professional)

    assert resolved.id == draft.id


def test_child_age_domain_validation_rejects_out_of_range_values():
    municipality = _create_municipality()
    professional = UserFactory()
    evaluation = AssessmentEvaluation(
        professional=professional,
        municipality=municipality,
        status=constants.EVALUATION_STATUS_DRAFT,
        is_active=True,
        child_age=19,
    )

    with pytest.raises(ValidationError):
        evaluation.full_clean()


def test_super_admin_revoking_user_access_removes_operational_access(client):
    municipality = _create_municipality()
    admin = UserFactory(is_superuser=True, is_staff=True)
    professional = UserFactory(is_superuser=False, is_staff=False)

    ensure_assessment_groups()
    professional_group = Group.objects.get(name=constants.ROLE_PROFESSIONAL)
    professional.groups.add(professional_group)

    profile = ProfessionalProfile.objects.create(
        user=professional,
        municipality=municipality,
        is_active=True,
    )

    client.force_login(admin)
    response = client.post(
        reverse("assessments:settings_professionals_action"),
        data={
            "profile_id": str(profile.id),
            "action": PROFESSIONAL_ACTION_REVOKE_ACCESS,
        },
    )

    assert response.status_code == HTTPStatus.FOUND

    professional.refresh_from_db()
    assert not professional.groups.filter(name=constants.ROLE_PROFESSIONAL).exists()
    assert not professional.groups.filter(name=constants.ROLE_CHIEF_ADMIN).exists()

    client.force_login(professional)
    forbidden_response = client.get(reverse("assessments:settings_access"))
    assert forbidden_response.status_code == HTTPStatus.FORBIDDEN


def test_deleting_user_cascades_professional_profile():
    municipality = _create_municipality()
    professional = UserFactory()
    profile = ProfessionalProfile.objects.create(
        user=professional,
        municipality=municipality,
        is_active=True,
    )

    professional_id = professional.id
    profile_id = profile.id

    professional.delete()

    assert not ProfessionalProfile.objects.filter(id=profile_id).exists()
    assert not ProfessionalProfile.objects.filter(user_id=professional_id).exists()
