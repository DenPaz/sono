from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.assessments import constants
from apps.assessments.forms.questionnaire import QuestionnaireBlock1Form
from apps.assessments.forms.questionnaire import QuestionnaireBlock2Form
from apps.assessments.forms.questionnaire import QuestionnaireBlock3Form
from apps.assessments.forms.questionnaire import QuestionnaireBlock4ReviewForm
from apps.assessments.forms.questionnaire import QuestionnaireIdentificationForm
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.services.capabilities import get_assessment_capabilities
from apps.assessments.services.questionnaire_workflow import (
    get_or_create_draft_evaluation,
)
from apps.assessments.services.questionnaire_workflow import get_progress_percent
from apps.assessments.services.questionnaire_workflow import get_step_answers
from apps.assessments.services.questionnaire_workflow import (
    is_evaluation_visible_to_user,
)
from apps.assessments.views.mixins import AssessmentsCapabilityMixin

STEP_TEMPLATE_MAP = {
    0: "assessments/questionnaire/partials/step_identification.html",
    1: "assessments/questionnaire/partials/step_block_1.html",
    2: "assessments/questionnaire/partials/step_block_2.html",
    3: "assessments/questionnaire/partials/step_block_3.html",
    4: "assessments/questionnaire/partials/step_block_4_review.html",
}

STEP_FORM_CLASS_MAP = {
    0: QuestionnaireIdentificationForm,
    1: QuestionnaireBlock1Form,
    2: QuestionnaireBlock2Form,
    3: QuestionnaireBlock3Form,
    4: QuestionnaireBlock4ReviewForm,
}


def validate_step_or_404(step: int) -> int:
    if step not in STEP_FORM_CLASS_MAP:
        raise Http404(_("Passo de questionário inválido."))
    return step


def get_subscale_results_for_template(
    *, evaluation: AssessmentEvaluation
) -> list[dict[str, object]]:
    subscale_scores = evaluation.subscale_scores
    if not isinstance(subscale_scores, dict):
        return []

    subscale_results: list[dict[str, object]] = []
    for key in constants.EDSC_SUBSCALE_DEFINITIONS:
        payload = subscale_scores.get(key)
        if not isinstance(payload, dict):
            continue

        item_indexes = payload.get("item_indexes") or ()
        if isinstance(item_indexes, (list, tuple)):
            item_indexes_text = ", ".join(str(item) for item in item_indexes)
        else:
            item_indexes_text = str(item_indexes)

        subscale_results.append(
            {
                "title": payload.get("label")
                or str(constants.EDSC_SUBSCALE_DEFINITIONS[key]["label"]),
                "score": payload.get("score", 0),
                "acceptable_max": payload.get("acceptable_max", 0),
                "is_alert": bool(payload.get("is_alert", False)),
                "item_indexes": item_indexes_text,
            }
        )

    return subscale_results


def get_questionnaire_step_template(*, step: int) -> str:
    step = validate_step_or_404(step)
    return STEP_TEMPLATE_MAP[step]


def get_step_form(
    *,
    step: int,
    evaluation: AssessmentEvaluation,
    data: dict[str, object] | None = None,
    user=None,
    capabilities: dict[str, bool] | None = None,
):
    step = validate_step_or_404(step)
    form_class = STEP_FORM_CLASS_MAP[step]
    if step == constants.WIZARD_IDENTIFICATION_STEP:
        return form_class(
            data=data,
            instance=evaluation,
            user=user,
            capabilities=capabilities,
        )

    answers = get_step_answers(
        evaluation=evaluation,
        item_indexes=constants.WIZARD_STEP_ITEM_INDEXES[step],
    )
    return form_class(data=data, answers=answers)


def get_visible_evaluation_or_403(*, request, evaluation_id) -> AssessmentEvaluation:
    evaluation = get_object_or_404(
        AssessmentEvaluation.objects.select_related(
            "professional",
            "municipality",
        ),
        id=evaluation_id,
        is_active=True,
    )

    capabilities = get_assessment_capabilities(user=request.user)
    can_see = is_evaluation_visible_to_user(
        evaluation=evaluation,
        user=request.user,
        can_view_all_assessments=capabilities.get(
            constants.CAPABILITY_VIEW_ALL_ASSESSMENTS,
            False,
        ),
    )
    if not can_see:
        raise PermissionDenied
    return evaluation


class EvaluationCreateOrResumeView(AssessmentsCapabilityMixin, View):
    def get(self, request, *args, **kwargs):
        evaluation = get_or_create_draft_evaluation(user=request.user)
        return redirect("assessments:evaluation_detail", evaluation_id=evaluation.id)


class EvaluationDetailView(AssessmentsCapabilityMixin, TemplateView):
    template_name = "assessments/questionnaire/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evaluation = get_visible_evaluation_or_403(
            request=self.request,
            evaluation_id=self.kwargs["evaluation_id"],
        )

        if evaluation.status == constants.EVALUATION_STATUS_DRAFT:
            current_step = evaluation.current_step
            form = get_step_form(
                step=current_step,
                evaluation=evaluation,
                user=self.request.user,
                capabilities=self.assessment_capabilities,
            )
            context["step_template"] = get_questionnaire_step_template(
                step=current_step
            )
            context["form"] = form
            context["current_step"] = current_step
            context["progress_percent"] = get_progress_percent(
                current_step=current_step
            )
        else:
            context["step_template"] = (
                "assessments/questionnaire/partials/result_summary.html"
            )
            context["current_step"] = constants.WIZARD_TOTAL_STEPS - 1
            context["progress_percent"] = 100
            context["subscale_results"] = get_subscale_results_for_template(
                evaluation=evaluation
            )

        context["evaluation"] = evaluation
        context["page_title"] = _("Questionário EDSC")
        return context
