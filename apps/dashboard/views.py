import csv
from collections import Counter
from collections import defaultdict
from datetime import timedelta

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView
from django.views.generic import TemplateView

from apps.assessments.utils import build_risk_summary
from apps.core.utils import generate_simple_pdf
from apps.core.viewmixins import AllowedRolesMixin
from apps.patients.models import Patient
from apps.patients.models import QuestionnaireResponse
from apps.users.enums import UserRole
from apps.users.models import Admin
from apps.users.models import Parent
from apps.users.models import Specialist
from apps.users.models import User
from apps.users.utils import send_invitation_email

HIGH_RISK_FLAG_THRESHOLD = 3


class IndexView(TemplateView):
    template_name = "dashboard/index.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.role = request.user.role

    def get_template_names(self):
        template_name = {
            UserRole.ADMIN: "dashboard/admin.html",
            UserRole.SPECIALIST: "dashboard/specialist.html",
            UserRole.PARENT: "dashboard/parent.html",
        }.get(self.role, self.template_name)
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handler = {
            UserRole.ADMIN: self._admin_context,
            UserRole.SPECIALIST: self._specialist_context,
            UserRole.PARENT: self._parent_context,
        }.get(self.role)
        if handler:
            context.update(handler())
        return context

    def _admin_context(self):
        recent_responses = QuestionnaireResponse.objects.select_related(
            "patient"
        ).order_by("-created")[:8]
        return {
            "stats": {
                "admins": Admin.objects.count(),
                "specialists": Specialist.objects.count(),
                "parents": Parent.objects.count(),
                "patients": Patient.objects.active().count(),
            },
            "recent_responses": recent_responses,
        }

    def _specialist_context(self):
        user = self.request.user
        recent_responses = (
            QuestionnaireResponse.objects.filter(patient__specialist=user)
            .select_related("patient")
            .order_by("-created")[:8]
        )
        return {
            "patient_count": Patient.objects.filter(
                specialist=user, is_active=True
            ).count(),
            "recent_responses": recent_responses,
        }

    def _parent_context(self):
        user = self.request.user
        patients = Patient.objects.filter(parent=user, is_active=True).prefetch_related(
            "questionnaire_responses"
        )
        recent_responses = (
            QuestionnaireResponse.objects.filter(patient__parent=user)
            .select_related("patient")
            .order_by("-created")[:5]
        )
        return {
            "patients": patients,
            "recent_responses": recent_responses,
        }


def _matches_filter(value: str, expected: str) -> bool:
    if not expected:
        return True
    return expected.lower() in str(value).lower()


def _get_patient_city(patient) -> str:
    if not patient:
        return "-"
    parent = getattr(patient, "parent", None)
    profile = getattr(parent, "profile", None) if parent else None
    address = getattr(profile, "address", None) or {}
    return address.get("city") or "-"


def _get_municipality(response: QuestionnaireResponse) -> str:
    if response.municipality:
        return response.municipality
    return _get_patient_city(response.patient)


def _get_professional_name(response: QuestionnaireResponse) -> str:
    if response.professional:
        return response.professional.get_full_name()
    # Fallback to the patient's assigned specialist
    patient = response.patient
    specialist = getattr(patient, "specialist", None) if patient else None
    return specialist.get_full_name() if specialist else "-"


def _build_evaluation_row(response: QuestionnaireResponse) -> dict:
    risk = build_risk_summary(response.flags)
    status = _("Em revisão") if response.has_flags else _("Concluída")
    return {
        "id": f"EDSC-{str(response.pk)[:8]}",
        "assessment_id": response.pk,
        "patient": response.patient_display_name,
        "professional": _get_professional_name(response),
        "municipality": _get_municipality(response),
        "score": response.total_score,
        "risk": str(risk["label"]),
        "status": status,
        "updated_at": response.modified.strftime("%Y-%m-%d"),
    }


def _build_evaluations(responses: list[QuestionnaireResponse]) -> list[dict]:
    return [_build_evaluation_row(response) for response in responses]


def _filter_evaluations(
    evaluations: list[dict],
    patient: str,
    professional: str,
    status: str,
    risk: str,
) -> list[dict]:
    return [
        item
        for item in evaluations
        if _matches_filter(item["patient"], patient)
        and _matches_filter(item["professional"], professional)
        and _matches_filter(item["status"], status)
        and _matches_filter(item["risk"], risk)
    ]


def _resolve_period(selected_period: str) -> str:
    return selected_period if selected_period in {"7d", "30d", "90d"} else "30d"


def _build_period_buckets(selected_period: str, today) -> list[dict]:
    if selected_period == "7d":
        start_date = today - timedelta(days=6)
        return [
            {
                "label": (start_date + timedelta(days=offset)).strftime("%d/%m"),
                "start": start_date + timedelta(days=offset),
                "end": start_date + timedelta(days=offset),
            }
            for offset in range(7)
        ]

    if selected_period == "90d":
        start_date = today - timedelta(days=89)
        buckets = []
        for index in range(3):
            bucket_start = start_date + timedelta(days=index * 30)
            bucket_end = min(bucket_start + timedelta(days=29), today)
            buckets.append(
                {
                    "label": bucket_start.strftime("%b"),
                    "start": bucket_start,
                    "end": bucket_end,
                }
            )
        return buckets

    start_date = today - timedelta(days=29)
    bucket_count = (30 + 6) // 7
    buckets = []
    for index in range(bucket_count):
        bucket_start = start_date + timedelta(days=index * 7)
        bucket_end = min(bucket_start + timedelta(days=6), today)
        buckets.append(
            {
                "label": f"Sem {index + 1}",
                "start": bucket_start,
                "end": bucket_end,
            }
        )
    return buckets


def _build_report_payload(selected_period: str) -> dict:
    today = timezone.localdate()
    period = _resolve_period(selected_period)
    days_map = {"7d": 6, "30d": 29, "90d": 89}
    start_date = today - timedelta(days=days_map[period])

    queryset = QuestionnaireResponse.objects.filter(
        created__date__range=(start_date, today)
    ).select_related(
        "patient",
        "patient__parent",
        "patient__parent__parent_profile",
    )
    responses = list(queryset)
    buckets = _build_period_buckets(period, today)

    bucket_stats = [
        {"count": 0, "score_sum": 0} for _ in range(len(buckets))
    ]
    for response in responses:
        response_date = response.created.date()
        for index, bucket in enumerate(buckets):
            if bucket["start"] <= response_date <= bucket["end"]:
                bucket_stats[index]["count"] += 1
                bucket_stats[index]["score_sum"] += response.total_score
                break

    bar_series = []
    line_series = []
    for index, bucket in enumerate(buckets):
        count = bucket_stats[index]["count"]
        average = (
            round(bucket_stats[index]["score_sum"] / count, 1) if count else 0
        )
        bar_series.append({"label": bucket["label"], "value": count})
        line_series.append({"label": bucket["label"], "value": average})

    total_patients = Patient.objects.active().count()
    unique_patients = len({response.patient_id for response in responses})
    high_risk_count = sum(
        1
        for response in responses
        if sum(1 for value in response.flags.values() if value)
        >= HIGH_RISK_FLAG_THRESHOLD
    )
    high_risk_pct = (
        round((high_risk_count / len(responses)) * 100)
        if responses
        else 0
    )
    average_score = (
        round(sum(response.total_score for response in responses) / len(responses), 1)
        if responses
        else 0
    )
    coverage_pct = (
        round((unique_patients / total_patients) * 100)
        if total_patients
        else 0
    )

    metrics = [
        {"label": _("Avaliações no período"), "value": str(len(responses))},
        {"label": _("Risco alto"), "value": f"{high_risk_pct}%"},
        {"label": _("Pacientes avaliados"), "value": str(unique_patients)},
        {"label": _("Cobertura"), "value": f"{coverage_pct}%"},
        {"label": _("Pontuação média"), "value": str(average_score)},
    ]

    return {
        "period": period,
        "start_date": start_date,
        "end_date": today,
        "responses": responses,
        "metrics": metrics,
        "bar_series": bar_series,
        "line_series": line_series,
    }


class EvaluationsListView(AllowedRolesMixin, TemplateView):
    template_name = "evaluations/index.html"
    allowed_roles = [UserRole.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.GET.get("patient", "")
        professional = self.request.GET.get("professional", "")
        status = self.request.GET.get("status", "")
        risk = self.request.GET.get("risk", "")

        responses = list(
            QuestionnaireResponse.objects.select_related(
                "patient",
                "patient__parent",
                "patient__parent__parent_profile",
                "patient__specialist",
            ).order_by("-created")
        )
        evaluations = _build_evaluations(responses)
        filtered = _filter_evaluations(
            evaluations,
            patient=patient,
            professional=professional,
            status=status,
            risk=risk,
        )

        context.update(
            {
                "page_title": _("Gestao de avaliacoes"),
                "evaluations": filtered,
                "applied_filters": {
                    "patient": patient,
                    "professional": professional,
                    "status": status,
                    "risk": risk,
                },
                "status_options": sorted({item["status"] for item in evaluations}),
                "risk_options": sorted({item["risk"] for item in evaluations}),
            }
        )
        return context


class EvaluationsCsvExportView(AllowedRolesMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def get(self, request, *args, **kwargs):
        patient = request.GET.get("patient", "")
        professional = request.GET.get("professional", "")
        status = request.GET.get("status", "")
        risk = request.GET.get("risk", "")

        responses = list(
            QuestionnaireResponse.objects.select_related(
                "patient",
                "patient__parent",
                "patient__parent__parent_profile",
                "patient__specialist",
            ).order_by("-created")
        )
        evaluations = _build_evaluations(responses)
        filtered = _filter_evaluations(
            evaluations,
            patient=patient,
            professional=professional,
            status=status,
            risk=risk,
        )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="avaliacoes.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "código",
                "paciente",
                "profissional",
                "município",
                "pontuação",
                "risco",
                "status",
                "atualizado_em",
            ]
        )
        for item in filtered:
            writer.writerow(
                [
                    item["id"],
                    item["patient"],
                    item["professional"],
                    item["municipality"],
                    item["score"],
                    item["risk"],
                    item["status"],
                    item["updated_at"],
                ]
            )
        return response


class InviteProfessionalForm(forms.Form):
    name = forms.CharField(
        label=_("Nome"),
        max_length=150,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full"}),
    )
    email = forms.EmailField(
        label=_("E-mail"),
        widget=forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Ja existe um usuario com este e-mail."))
        return email

    def save(self) -> Specialist:
        parts = self.cleaned_data["name"].split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else _("Especialista")
        specialist = Specialist(
            first_name=first_name,
            last_name=last_name,
            email=self.cleaned_data["email"],
        )
        specialist.set_unusable_password()
        specialist.save()
        return specialist


class ProfessionalsListView(AllowedRolesMixin, TemplateView):
    template_name = "professionals/index.html"
    allowed_roles = [UserRole.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query", "")
        role = self.request.GET.get("role", "")
        status = self.request.GET.get("status", "")

        specialists = list(
            Specialist.objects.order_by("first_name", "last_name")
        )
        patients = list(
            Patient.objects.filter(is_active=True)
            .select_related("parent", "parent__parent_profile", "specialist")
            .order_by("first_name", "last_name")
        )
        patients_by_specialist = defaultdict(list)
        for patient in patients:
            if patient.specialist_id:
                patients_by_specialist[patient.specialist_id].append(patient)

        professionals = []
        for specialist in specialists:
            assigned_patients = patients_by_specialist.get(specialist.pk, [])
            city_counts = Counter(
                _get_patient_city(patient)
                for patient in assigned_patients
                if _get_patient_city(patient) != "-"
            )
            municipality = city_counts.most_common(1)[0][0] if city_counts else "-"
            role_label = _("Especialista")
            status_label = _("Ativo") if specialist.is_active else _("Inativo")

            professionals.append(
                {
                    "name": specialist.get_full_name(),
                    "email": specialist.email,
                    "role": role_label,
                    "status": status_label,
                    "active_cases": len(assigned_patients),
                    "municipality": municipality,
                }
            )

        filtered = [
            item
            for item in professionals
            if (
                _matches_filter(item["name"], query)
                or _matches_filter(item["email"], query)
                or not query
            )
            and _matches_filter(item["role"], role)
            and _matches_filter(item["status"], status)
        ]

        context.update(
            {
                "page_title": _("Gestão de Profissionais"),
                "professionals": filtered,
                "applied_filters": {"query": query, "role": role, "status": status},
                "role_options": sorted({item["role"] for item in professionals}),
                "status_options": sorted({item["status"] for item in professionals}),
            }
        )
        return context


class ProfessionalManageView(AllowedRolesMixin, TemplateView):
    template_name = "professionals/manage.html"
    allowed_roles = [UserRole.ADMIN]

    def _get_selected_email(self) -> str:
        return self.request.GET.get("email", "").strip()

    def _find_specialist(self, email: str):
        return Specialist.objects.filter(email__iexact=email).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_email = self._get_selected_email()
        specialist = (
            self._find_specialist(selected_email) if selected_email else None
        )

        professional = None
        if specialist:
            assigned_patients = list(
                Patient.objects.filter(specialist=specialist, is_active=True)
                .select_related("parent", "parent__parent_profile")
                .order_by("first_name", "last_name")
            )
            city_counts = Counter(
                _get_patient_city(patient)
                for patient in assigned_patients
                if _get_patient_city(patient) != "-"
            )
            role_label = _("Especialista")
            status_label = _("Ativo") if specialist.is_active else _("Inativo")
            professional = {
                "name": specialist.get_full_name(),
                "email": specialist.email,
                "role": role_label,
                "status_label": status_label,
                "status_value": "active" if specialist.is_active else "inactive",
                "active_cases": len(assigned_patients),
                "municipality": (
                    city_counts.most_common(1)[0][0] if city_counts else "-"
                ),
            }

        context.update(
            {
                "page_title": _("Gerenciar profissional"),
                "selected_email": selected_email,
                "professional": professional,
                "professional_not_found": selected_email and specialist is None,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        specialist = self._find_specialist(email) if email else None

        if specialist:
            name = request.POST.get("name", "").strip()
            if name:
                parts = name.split()
                specialist.first_name = parts[0]
                if len(parts) > 1:
                    specialist.last_name = " ".join(parts[1:])
                else:
                    specialist.last_name = ""
            specialist.is_active = request.POST.get("status") == "active"
            specialist.save(update_fields=["first_name", "last_name", "is_active"])
            messages.success(
                request,
                _("Atualização registrada para %(name)s.")
                % {"name": specialist.get_full_name()},
            )
        else:
            messages.warning(
                request,
                _("Não foi possível identificar o profissional selecionado."),
            )

        params = f"email={email}" if email else ""
        target = reverse("dashboard:manage_professional")
        return redirect(f"{target}?{params}" if params else target)


class InviteProfessionalView(AllowedRolesMixin, FormView):
    template_name = "professionals/invite.html"
    form_class = InviteProfessionalForm
    success_url = reverse_lazy("dashboard:professionals")
    allowed_roles = [UserRole.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Convidar profissional")
        return context

    def form_valid(self, form):
        specialist = form.save()
        send_invitation_email(self.request, specialist)
        messages.success(
            self.request,
            _("Convite enviado para %(email)s.")
            % {"email": form.cleaned_data["email"]},
        )
        return super().form_valid(form)


class MunicipalitiesView(AllowedRolesMixin, TemplateView):
    template_name = "municipalities/index.html"
    allowed_roles = [UserRole.ADMIN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query", "")
        today = timezone.localdate()
        recent_start = today - timedelta(days=29)
        previous_start = recent_start - timedelta(days=30)
        previous_end = recent_start - timedelta(days=1)

        responses = QuestionnaireResponse.objects.select_related(
            "patient",
            "patient__parent",
            "patient__parent__parent_profile",
        )

        city_stats = defaultdict(
            lambda: {
                "completed": 0,
                "high_risk": 0,
                "recent": 0,
                "previous": 0,
                "unique_patients": set(),
            }
        )

        for response in responses:
            city = _get_municipality(response)
            if city == "-":
                continue
            stats = city_stats[city]
            stats["completed"] += 1
            stats["unique_patients"].add(response.patient_id or response.patient_name)

            flagged_count = sum(1 for value in response.flags.values() if value)
            if flagged_count >= HIGH_RISK_FLAG_THRESHOLD:
                stats["high_risk"] += 1

            response_date = response.created.date()
            if response_date >= recent_start:
                stats["recent"] += 1
            elif previous_start <= response_date <= previous_end:
                stats["previous"] += 1

        municipalities = []
        for city, stats in city_stats.items():
            if stats["previous"] == 0:
                trend = "+100%" if stats["recent"] else "0%"
            else:
                delta = (
                    (stats["recent"] - stats["previous"]) / stats["previous"]
                ) * 100
                trend = f"{delta:+.0f}%"

            municipalities.append(
                {
                    "name": city,
                    "coverage": 100,  # Placeholder as we now support dynamic entries
                    "completed": stats["completed"],
                    "high_risk": stats["high_risk"],
                    "trend": trend,
                }
            )

        ranking = sorted(
            [item for item in municipalities if _matches_filter(item["name"], query)],
            key=lambda item: item["coverage"],
            reverse=True,
        )
        context.update(
            {
                "page_title": _("Desempenho por Município"),
                "municipalities": ranking,
                "query": query,
                "highlights": [
                    {
                        "label": _("Total de Municípios"),
                        "value": str(len(ranking)),
                    },
                    {
                        "label": _("Município líder"),
                        "value": ranking[0]["name"] if ranking else "-",
                    },
                    {
                        "label": _("Avaliações concluídas"),
                        "value": str(
                            sum(item["completed"] for item in ranking)
                            if ranking
                            else 0
                        ),
                    },
                ],
            }
        )
        return context


class ReportsView(AllowedRolesMixin, TemplateView):
    template_name = "reports/index.html"
    allowed_roles = [UserRole.ADMIN]

    PERIOD_OPTIONS = [
        ("7d", _("Ultimos 7 dias")),
        ("30d", _("Ultimos 30 dias")),
        ("90d", _("Ultimos 90 dias")),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_period = _resolve_period(self.request.GET.get("period", "30d"))
        payload = _build_report_payload(selected_period)

        context.update(
            {
                "page_title": _("Relatorios Consolidados"),
                "selected_period": payload["period"],
                "period_options": self.PERIOD_OPTIONS,
                "metrics": payload["metrics"],
                "bar_series": payload["bar_series"],
                "line_series": payload["line_series"],
                "bar_max": max(
                    (item["value"] for item in payload["bar_series"]),
                    default=0,
                ),
                "line_max": max(
                    (item["value"] for item in payload["line_series"]),
                    default=0,
                ),
            }
        )
        return context


class ReportsPdfExportView(AllowedRolesMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def get(self, request, *args, **kwargs):
        selected_period = _resolve_period(request.GET.get("period", "30d"))
        payload = _build_report_payload(selected_period)

        lines = [
            f"Período: {selected_period}",
            "",
            "Métricas:",
        ]
        lines.extend(
            [f"- {metric['label']}: {metric['value']}" for metric in payload["metrics"]]
        )

        lines.extend(["", "Volume de avaliações:"])
        lines.extend(
            [f"- {point['label']}: {point['value']}" for point in payload["bar_series"]]
        )

        lines.extend(["", "Média de pontuação clínica:"])
        lines.extend(
            [
                f"- {point['label']}: {point['value']}"
                for point in payload["line_series"]
            ]
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorios-{selected_period}.pdf"'
        )
        response.write(generate_simple_pdf("Relatorios consolidados", lines))
        return response


class ReportsCsvExportView(AllowedRolesMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def get(self, request, *args, **kwargs):
        selected_period = _resolve_period(request.GET.get("period", "30d"))
        payload = _build_report_payload(selected_period)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorios-{selected_period}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["periodo", selected_period])
        writer.writerow([])
        writer.writerow(["metrica", "valor"])
        for metric in payload["metrics"]:
            writer.writerow([metric["label"], metric["value"]])

        writer.writerow([])
        writer.writerow(["serie", "periodo", "valor"])
        for point in payload["bar_series"]:
            writer.writerow(["volume_avaliacoes", point["label"], point["value"]])
        for point in payload["line_series"]:
            writer.writerow(["media_score_clinico", point["label"], point["value"]])
        return response
