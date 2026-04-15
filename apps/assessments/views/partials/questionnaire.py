from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.assessments import constants
from apps.assessments.services.capabilities import get_assessment_capabilities
from apps.assessments.services.questionnaire_workflow import finalize_questionnaire
from apps.assessments.services.questionnaire_workflow import get_progress_percent
from apps.assessments.services.questionnaire_workflow import persist_identification_step
from apps.assessments.services.questionnaire_workflow import (
    persist_questionnaire_step_answers,
)
from apps.assessments.views.questionnaire import get_questionnaire_step_template
from apps.assessments.views.questionnaire import get_step_form
from apps.assessments.views.questionnaire import get_subscale_results_for_template
from apps.assessments.views.questionnaire import get_visible_evaluation_or_403
from apps.assessments.views.questionnaire import validate_step_or_404


class QuestionnaireStepPartialView(View):
    def post(self, request, *args, **kwargs):
        step = kwargs["step"]
        evaluation_id = request.POST.get("evaluation_id")
        action = request.POST.get("action", "next")
        capabilities = get_assessment_capabilities(user=request.user)
        evaluation = get_visible_evaluation_or_403(
            request=request,
            evaluation_id=evaluation_id,
        )
        if evaluation.status != constants.EVALUATION_STATUS_DRAFT:
            raise PermissionDenied(
                _("Esta avaliação já foi finalizada e não pode ser alterada.")
            )

        if action == "back":
            target_step = validate_step_or_404(
                max(step - 1, constants.WIZARD_IDENTIFICATION_STEP)
            )
            evaluation.current_step = target_step
            evaluation.save(update_fields=["current_step", "modified"])
            form = get_step_form(
                step=target_step,
                evaluation=evaluation,
                user=request.user,
                capabilities=capabilities,
            )
            return self.render_step(
                request=request,
                evaluation=evaluation,
                step=target_step,
                form=form,
            )

        form = get_step_form(
            step=step,
            evaluation=evaluation,
            data=request.POST,
            user=request.user,
            capabilities=capabilities,
        )

        if not form.is_valid():
            return self.render_step(
                request=request,
                evaluation=evaluation,
                step=step,
                form=form,
                status=422,
            )

        if step == constants.WIZARD_IDENTIFICATION_STEP:
            persist_identification_step(
                evaluation=evaluation,
                cleaned_data=form.cleaned_data,
            )
            next_step = 1
            form = get_step_form(
                step=next_step,
                evaluation=evaluation,
                user=request.user,
                capabilities=capabilities,
            )
            return self.render_step(
                request=request,
                evaluation=evaluation,
                step=next_step,
                form=form,
            )

        persist_questionnaire_step_answers(
            evaluation=evaluation,
            cleaned_answers=form.cleaned_answers(),
            next_step=(
                step
                if action == "finish"
                else min(step + 1, constants.WIZARD_TOTAL_STEPS - 1)
            ),
        )

        if action == "finish":
            try:
                finalize_questionnaire(evaluation=evaluation)
            except ValueError as exc:
                form.add_error(None, str(exc))
                messages.error(request, _("Revise as respostas antes de finalizar."))
                return self.render_step(
                    request=request,
                    evaluation=evaluation,
                    step=step,
                    form=form,
                    status=422,
                )

            messages.success(request, _("Questionário concluído com sucesso."))
            return render(
                request=request,
                template_name="assessments/questionnaire/partials/result_summary.html",
                context={
                    "evaluation": evaluation,
                    "current_step": constants.WIZARD_TOTAL_STEPS - 1,
                    "progress_percent": 100,
                    "subscale_results": get_subscale_results_for_template(
                        evaluation=evaluation
                    ),
                },
            )

        next_step = min(step + 1, constants.WIZARD_TOTAL_STEPS - 1)
        form = get_step_form(
            step=next_step,
            evaluation=evaluation,
            user=request.user,
            capabilities=capabilities,
        )
        return self.render_step(
            request=request,
            evaluation=evaluation,
            step=next_step,
            form=form,
        )

    def render_step(self, *, request, evaluation, step: int, form, status: int = 200):
        return render(
            request=request,
            template_name=get_questionnaire_step_template(step=step),
            context={
                "evaluation": evaluation,
                "form": form,
                "current_step": step,
                "progress_percent": get_progress_percent(current_step=step),
            },
            status=status,
        )
