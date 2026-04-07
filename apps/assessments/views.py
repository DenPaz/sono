# pyright: reportMissingImports=false

from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView

from apps.core.utils import generate_simple_pdf

from .forms import SUBSCALE_GROUPS
from .forms import SUBSCALE_LABELS
from .forms import BlockOneForm
from .forms import BlockTwoForm
from .forms import PatientDataForm

QUESTIONNAIRE_FORMS = [
    ("patient", PatientDataForm),
    ("screening", BlockOneForm),
    ("edsc", BlockTwoForm),
]

STEP_METADATA = {
    "patient": {
        "title": _("Identificacao do Paciente"),
        "description": _("Dados cadastrais e contexto assistencial."),
    },
    "screening": {
        "title": _("Bloco 1 - Triagem"),
        "description": _("Duas perguntas de validacao inicial."),
    },
    "edsc": {
        "title": _("Bloco 2 - Escala EDSC"),
        "description": _("Vinte e quatro perguntas com escala de frequencia."),
    },
}

HIGH_RISK_SCORE_THRESHOLD = 48
MODERATE_RISK_SCORE_THRESHOLD = 30
SCREENING_HIGH_RISK_THRESHOLD = 2
SCREENING_MODERATE_RISK_THRESHOLD = 1
MAX_SUBSCALE_ITEM_SCORE = 3


def _classify_risk(total_score: int, screening_positive: int) -> dict:
    if (
        total_score >= HIGH_RISK_SCORE_THRESHOLD
        or screening_positive == SCREENING_HIGH_RISK_THRESHOLD
    ):
        return {
            "label": _("Alto"),
            "badge": "badge-error",
            "description": _("Risco elevado. Priorizar avaliacao clinica imediata."),
        }
    if (
        total_score >= MODERATE_RISK_SCORE_THRESHOLD
        or screening_positive == SCREENING_MODERATE_RISK_THRESHOLD
    ):
        return {
            "label": _("Moderado"),
            "badge": "badge-warning",
            "description": _("Risco moderado. Recomendado acompanhamento continuado."),
        }
    return {
        "label": _("Baixo"),
        "badge": "badge-success",
        "description": _("Risco baixo. Monitoramento e orientacoes preventivas."),
    }


def _build_subscale_scores(block_two_data: dict) -> list[dict]:
    subscales = []
    for subscale_key, question_keys in SUBSCALE_GROUPS.items():
        max_score = len(question_keys) * MAX_SUBSCALE_ITEM_SCORE
        score = sum(
            int(block_two_data.get(question_key, 0))
            for question_key in question_keys
        )
        percentage = round((score / max_score) * 100) if max_score else 0
        subscales.append(
            {
                "key": subscale_key,
                "label": SUBSCALE_LABELS[subscale_key],
                "score": score,
                "max_score": max_score,
                "percentage": percentage,
            },
        )
    return subscales


def _build_assessment_payload(cleaned_data_by_step: dict, assessment_id: str) -> dict:
    patient_data = cleaned_data_by_step["patient"]
    screening_data = cleaned_data_by_step["screening"]
    block_two_data = cleaned_data_by_step["edsc"]

    subscales = _build_subscale_scores(block_two_data)
    total_score = sum(item["score"] for item in subscales)
    screening_positive = sum(
        value == "sim"
        for value in (
            screening_data.get("screening_q1"),
            screening_data.get("screening_q2"),
        )
    )
    risk = _classify_risk(
        total_score=total_score,
        screening_positive=screening_positive,
    )

    return {
        "assessment_id": assessment_id,
        "patient": {
            "name": patient_data["patient_name"],
            "birth_date": patient_data["patient_birth_date"].isoformat(),
            "municipality": patient_data["municipality"],
            "professional": patient_data["professional_name"],
        },
        "screening": screening_data,
        "subscales": subscales,
        "total_score": total_score,
        "max_score": 72,
        "risk": risk,
    }


class QuestionnaireWizardView(LoginRequiredMixin, SessionWizardView):
    template_name = "assessments/questionnaire.html"
    form_list = QUESTIONNAIRE_FORMS

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        form_keys = list(self.get_form_list().keys())
        current_step = self.steps.current
        current_step_index = form_keys.index(current_step) + 1

        wizard_steps = []
        for index, step_key in enumerate(form_keys, start=1):
            wizard_steps.append(
                {
                    "key": step_key,
                    "title": STEP_METADATA[step_key]["title"],
                    "description": STEP_METADATA[step_key]["description"],
                    "index": index,
                    "is_current": step_key == current_step,
                    "is_completed": index < current_step_index,
                },
            )

        progress_percent = round((current_step_index / len(form_keys)) * 100)
        context.update(
            {
                "page_title": _("Aplicacao do Questionario EDSC"),
                "wizard_steps": wizard_steps,
                "current_step_index": current_step_index,
                "total_steps": len(form_keys),
                "progress_percent": progress_percent,
            },
        )
        return context

    def done(self, form_list, **kwargs):
        cleaned_data_by_step = {
            step_name: form.cleaned_data
            for step_name, form in zip(
                self.get_form_list().keys(),
                form_list,
                strict=True,
            )
        }
        assessment_id = str(uuid4())
        assessment_payload = _build_assessment_payload(
            cleaned_data_by_step=cleaned_data_by_step,
            assessment_id=assessment_id,
        )

        stored_results = self.request.session.get("assessment_results", {})
        stored_results[assessment_id] = assessment_payload
        self.request.session["assessment_results"] = stored_results
        self.request.session.modified = True

        return redirect("assessments:results", assessment_id=assessment_id)


class AssessmentResultView(LoginRequiredMixin, TemplateView):
    template_name = "assessments/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment_id = str(self.kwargs["assessment_id"])
        stored_results = self.request.session.get("assessment_results", {})
        assessment = stored_results.get(assessment_id)

        if not assessment:
            context.update(
                {
                    "page_title": _("Resultado Clinico"),
                    "result_not_found": True,
                    "assessment": {
                        "assessment_id": assessment_id,
                        "patient": {
                            "name": _("Nao encontrado"),
                            "birth_date": "-",
                            "municipality": "-",
                            "professional": "-",
                        },
                        "total_score": 0,
                        "max_score": 72,
                        "risk": {
                            "label": _("Indisponivel"),
                            "badge": "badge-ghost",
                            "description": _(
                                "Nao foi possivel recuperar os dados desta avaliacao.",
                            ),
                        },
                        "subscales": [],
                    },
                },
            )
            return context

        subscales = assessment["subscales"]
        average_percentage = round(
            sum(item["percentage"] for item in subscales) / len(subscales),
            1,
        )
        context.update(
            {
                "page_title": _("Resultado Clinico"),
                "result_not_found": False,
                "assessment": assessment,
                "subscale_average": average_percentage,
            },
        )
        return context


class AssessmentResultPdfExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        assessment_id = str(kwargs["assessment_id"])
        stored_results = request.session.get("assessment_results", {})
        assessment = stored_results.get(assessment_id)

        if not assessment:
            messages.warning(
                request,
                _("Resultado nao encontrado para exportacao."),
            )
            return redirect("assessments:results", assessment_id=assessment_id)

        lines = [
            f"Avaliacao: {assessment_id}",
            f"Paciente: {assessment['patient']['name']}",
            f"Municipio: {assessment['patient']['municipality']}",
            f"Profissional: {assessment['patient']['professional']}",
            f"Score total: {assessment['total_score']}/{assessment['max_score']}",
            f"Risco: {assessment['risk']['label']}",
            "",
            "Subescalas:",
        ]

        for subscale in assessment["subscales"]:
            lines.append(
                (
                    f"- {subscale['label']}: {subscale['score']}/"
                    f"{subscale['max_score']} ({subscale['percentage']}%)"
                )
            )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="resultado-{assessment_id}.pdf"'
        )
        response.write(generate_simple_pdf("Resultado clinico EDSC", lines))
        return response
