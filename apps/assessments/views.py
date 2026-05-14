from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView

from apps.core.utils import generate_simple_pdf
from apps.core.viewmixins import AllowedRolesMixin
from apps.patients.models import Patient, QuestionnaireResponse
from apps.users.enums import UserRole

from .forms import QUESTIONNAIRE_FORMS
from .forms import STEP_METADATA
from .utils import build_risk_summary
from .utils import build_subscale_breakdown
from .utils import TOTAL_MAX_SCORE


def _get_patient_city(patient) -> str:
    if not patient:
        return "-"
    parent = getattr(patient, "parent", None)
    profile = getattr(parent, "profile", None) if parent else None
    address = getattr(profile, "address", None) or {}
    return address.get("city") or "-"


class QuestionnaireWizardView(AllowedRolesMixin, SessionWizardView):
    template_name = "assessments/questionnaire.html"
    form_list = QUESTIONNAIRE_FORMS
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        form_keys = list(self.get_form_list().keys())
        current_step = self.steps.current
        current_step_index = form_keys.index(current_step) + 1

        wizard_steps = []
        for index, step_key in enumerate(form_keys, start=1):
            meta = STEP_METADATA.get(step_key, {})
            wizard_steps.append(
                {
                    "key": step_key,
                    "title": meta.get("title", step_key.title()),
                    "description": meta.get("description", ""),
                    "index": index,
                    "is_current": step_key == current_step,
                    "is_completed": index < current_step_index,
                }
            )

        progress_percent = round((current_step_index / len(form_keys)) * 100)
        
        all_cities = list(QuestionnaireResponse.objects.exclude(municipality="").values_list("municipality", flat=True).distinct())

        context.update(
            {
                "page_title": _("Aplicação do questionário"),
                "wizard_steps": wizard_steps,
                "current_step_index": current_step_index,
                "total_steps": len(form_keys),
                "progress_percent": progress_percent,
                "all_municipalities": all_cities,
            }
        )
        return context

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        first_name = cleaned_data.pop("first_name", "").strip()
        last_name = cleaned_data.pop("last_name", "").strip()
        parent = cleaned_data.pop("parent", None)
        birth_date = cleaned_data.pop("birth_date", None)
        biological_sex = cleaned_data.pop("biological_sex", None)
        municipality = cleaned_data.pop("municipality", "").strip()
        notes = cleaned_data.pop("notes", "").strip()

        if not first_name:
            messages.error(self.request, _("Informe o nome do paciente."))
            return redirect("assessments:questionnaire")

        # Try to find an existing patient with this name
        patient = Patient.objects.filter(
            first_name__iexact=first_name, last_name__iexact=last_name
        ).first()

        response = QuestionnaireResponse.objects.create(
            patient=patient,
            parent=parent,
            professional=self.request.user,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            biological_sex=biological_sex,
            municipality=municipality,
            notes=notes,
            **cleaned_data,
        )
        messages.success(self.request, _("Questionário registrado com sucesso."))
        return redirect("assessments:results", assessment_id=response.pk)


class AssessmentResultView(AllowedRolesMixin, TemplateView):
    template_name = "assessments/results.html"
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment_id = str(self.kwargs["assessment_id"])

        try:
            response = QuestionnaireResponse.objects.select_related(
                "patient",
                "patient__parent",
                "patient__parent__parent_profile",
                "patient__specialist",
            ).get(pk=assessment_id)
        except QuestionnaireResponse.DoesNotExist:
            context.update(
                {
                    "page_title": _("Resultado clínico"),
                    "result_not_found": True,
                    "assessment": {
                        "assessment_id": assessment_id,
                        "patient": {
                            "name": _("Não encontrado"),
                            "birth_date": "-",
                            "municipality": "-",
                            "professional": "-",
                        },
                        "total_score": 0,
                        "max_score": TOTAL_MAX_SCORE,
                        "risk": {
                            "label": _("Indisponível"),
                            "badge": "badge-ghost",
                            "description": _("Não foi possível recuperar os dados."),
                        },
                        "subscales": [],
                    },
                }
            )
            return context

        subscales = build_subscale_breakdown(response)
        risk = build_risk_summary(response.flags)
        patient = response.patient
        professional = (
            response.professional.get_full_name()
            if response.professional
            else (
                patient.specialist.get_full_name()
                if patient and patient.specialist
                else "-"
            )
        )
        municipality = response.municipality or _get_patient_city(patient)
        average_percentage = (
            round(
                sum(item["percentage"] for item in subscales) / len(subscales),
                1,
            )
            if subscales
            else 0
        )

        from apps.patients.forms import QUESTIONNAIRE_FORMS as PATIENT_FORMS
        from apps.patients.forms import STEP_TITLES
        detailed_answers = []
        for step_name, form_class in PATIENT_FORMS:
            form = form_class()
            step_answers = []
            for field_name, field in form.fields.items():
                value = getattr(response, field_name)
                display_value = dict(field.choices).get(value, value)
                step_answers.append({
                    "question": field.label,
                    "answer": display_value,
                })
            detailed_answers.append({
                "title": STEP_TITLES.get(step_name, step_name),
                "answers": step_answers,
            })

        DISORDER_LABELS = {
            "sleep_onset_maintenance": _("Início e Manutenção do Sono"),
            "respiratory": _("Distúrbios Respiratórios do Sono"),
            "arousal": _("Despertares"),
            "sleep_wake_transition": _("Transição Sono-Vigília"),
            "excessive_daytime_sleepiness": _("Sonolência Diurna Excessiva"),
            "hyperhidrosis": _("Hiperidrose do Sono"),
        }
        active_disorders = [DISORDER_LABELS.get(k, k) for k, v in response.flags.items() if v]

        context.update(
            {
                "page_title": _("Resultado clínico"),
                "result_not_found": False,
                "assessment": {
                    "assessment_id": assessment_id,
                    "patient": {
                        "name": response.patient_display_name,
                        "birth_date": (response.birth_date or (patient.birth_date if patient else None)).isoformat() if (response.birth_date or (patient and patient.birth_date)) else "-",
                        "sex": response.get_biological_sex_display() if response.biological_sex else (patient.get_biological_sex_display() if patient else "-"),
                        "municipality": municipality,
                        "professional": professional,
                        "notes": response.notes or (patient.notes if patient else ""),
                    },
                    "total_score": response.total_score,
                    "max_score": TOTAL_MAX_SCORE,
                    "risk": risk,
                    "subscales": subscales,
                    "detailed_answers": detailed_answers,
                    "active_disorders": active_disorders,
                },
                "subscale_average": average_percentage,
            }
        )
        return context


class AssessmentResultPdfExportView(AllowedRolesMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def get(self, request, *args, **kwargs):
        assessment_id = str(kwargs["assessment_id"])
        try:
            response = QuestionnaireResponse.objects.select_related(
                "patient",
                "patient__parent",
                "patient__parent__parent_profile",
                "patient__specialist",
            ).get(pk=assessment_id)
        except QuestionnaireResponse.DoesNotExist:
            messages.warning(
                request,
                _("Resultado não encontrado para exportação."),
            )
            return redirect("assessments:results", assessment_id=assessment_id)

        patient = response.patient
        professional = (
            response.professional.get_full_name()
            if response.professional
            else (
                patient.specialist.get_full_name()
                if patient and patient.specialist
                else "-"
            )
        )
        municipality = response.municipality or _get_patient_city(patient)
        risk = build_risk_summary(response.flags)
        subscales = build_subscale_breakdown(response)

        lines = [
            f"Avaliação: {assessment_id}",
            f"Paciente: {response.patient_display_name}",
            f"Município: {municipality}",
            f"Profissional: {professional}",
            f"Pontuação total: {response.total_score}/{TOTAL_MAX_SCORE}",
            f"Risco: {risk['label']}",
            "",
            "Subescalas:",
        ]

        for subscale in subscales:
            lines.append(
                (
                    f"- {subscale['label']}: {subscale['score']}/"
                    f"{subscale['max_score']} ({subscale['percentage']}%)"
                )
            )

        response_pdf = HttpResponse(content_type="application/pdf")
        response_pdf["Content-Disposition"] = (
            f'attachment; filename="resultado-{assessment_id}.pdf"'
        )
        response_pdf.write(generate_simple_pdf("Resultado clínico", lines))
        return response_pdf
