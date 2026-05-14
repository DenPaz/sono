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
from django.template.loader import render_to_string
from weasyprint import HTML

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
        patients = Patient.objects.filter(specialist=user, is_active=True).prefetch_related(
            "questionnaire_responses"
        )
        recent_responses = (
            QuestionnaireResponse.objects.filter(patient__specialist=user)
            .select_related("patient")
            .order_by("-created")[:8]
        )
        return {
            "patients": patients,
            "patient_count": patients.count(),
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


from datetime import datetime

def _build_period_buckets(start_date, end_date) -> list[dict]:
    delta_days = (end_date - start_date).days
    
    buckets = []
    if delta_days <= 14:
        for offset in range(delta_days + 1):
            day = start_date + timedelta(days=offset)
            buckets.append({"label": day.strftime("%d/%m"), "start": day, "end": day})
    elif delta_days <= 90:
        bucket_count = (delta_days + 6) // 7
        for index in range(bucket_count):
            bucket_start = start_date + timedelta(days=index * 7)
            bucket_end = min(bucket_start + timedelta(days=6), end_date)
            buckets.append({"label": f"Sem {index + 1}", "start": bucket_start, "end": bucket_end})
    else:
        bucket_count = (delta_days + 30) // 30
        for index in range(bucket_count):
            bucket_start = start_date + timedelta(days=index * 30)
            bucket_end = min(bucket_start + timedelta(days=29), end_date)
            buckets.append({"label": bucket_start.strftime("%b %y"), "start": bucket_start, "end": bucket_end})
    return buckets


def _build_report_payload(start_date_str: str, end_date_str: str, municipality: str) -> dict:
    today = timezone.localdate()
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        start_date = today - timedelta(days=29)
        
    try:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        end_date = today

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    queryset = QuestionnaireResponse.objects.filter(
        created__date__range=(start_date, end_date)
    ).select_related(
        "patient",
        "patient__parent",
        "patient__parent__parent_profile",
    )
    all_responses = list(queryset)
    
    responses = []
    for r in all_responses:
        if municipality and municipality != "-":
            if _get_municipality(r) != municipality:
                continue
        responses.append(r)

    buckets = _build_period_buckets(start_date, end_date)

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

    total_disorders = sum(sum(1 for v in r.flags.values() if v) for r in responses)

    total_patients = Patient.objects.active().count()
    if municipality and municipality != "-":
        total_patients = len({r.patient_id or r.patient_display_name for r in responses}) or 1
        
    unique_patients = len({response.patient_id or response.patient_display_name for response in responses})
    high_risk_count = sum(1 for response in responses if response.has_flags)
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

    metrics = [
        {"label": _("Avaliações"), "value": str(len(responses))},
        {"label": _("Distúrbios"), "value": str(total_disorders)},
        {"label": _("Risco alto"), "value": f"{high_risk_pct}%"},
        {"label": _("Pacientes avaliados"), "value": str(unique_patients)},
        {"label": _("Pontuação média"), "value": str(average_score)},
    ]

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "municipality": municipality,
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
            pref_municipality = (specialist.preferences or {}).get("municipality")
            if pref_municipality:
                municipality = pref_municipality
            else:
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

        all_cities = set()
        for resp in QuestionnaireResponse.objects.select_related("patient__parent__parent_profile"):
            city = _get_municipality(resp)
            if city and city != "-":
                all_cities.add(city)
        for pat in Patient.objects.filter(is_active=True).select_related("parent", "parent__parent_profile"):
            city = _get_patient_city(pat)
            if city and city != "-":
                all_cities.add(city)

        professional = None
        if specialist:
            assigned_patients = list(
                Patient.objects.filter(specialist=specialist, is_active=True)
                .select_related("parent", "parent__parent_profile")
                .order_by("first_name", "last_name")
            )
            pref_municipality = (specialist.preferences or {}).get("municipality")
            city_counts = Counter(
                _get_patient_city(patient)
                for patient in assigned_patients
                if _get_patient_city(patient) != "-"
            )
            resolved_municipality = pref_municipality or (
                city_counts.most_common(1)[0][0] if city_counts else "-"
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
                "municipality": resolved_municipality if resolved_municipality != "-" else "",
                "is_custom_not_in_list": resolved_municipality != "-" and resolved_municipality not in all_cities,
            }

        context.update(
            {
                "page_title": _("Gerenciar profissional"),
                "selected_email": selected_email,
                "professional": professional,
                "all_municipalities": sorted(all_cities),
                "professional_not_found": selected_email and specialist is None,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        original_email = request.POST.get("original_email", "").strip()
        specialist = self._find_specialist(original_email) if original_email else None

        if specialist:
            new_email = request.POST.get("email", "").strip()
            if new_email and new_email != specialist.email:
                if User.objects.filter(email__iexact=new_email).exclude(pk=specialist.pk).exists():
                    messages.error(request, _("O e-mail informado já está em uso."))
                    return redirect(f"{self.request.path}?email={original_email}")
                specialist.email = new_email

            name = request.POST.get("name", "").strip()
            if name:
                parts = name.split()
                specialist.first_name = parts[0]
                if len(parts) > 1:
                    specialist.last_name = " ".join(parts[1:])
                else:
                    specialist.last_name = ""
            specialist.is_active = request.POST.get("status") == "active"

            new_municipality = request.POST.get("municipality", "").strip()
            prefs = specialist.preferences or {}
            if new_municipality and new_municipality != "-":
                prefs["municipality"] = new_municipality
            else:
                prefs.pop("municipality", None)
            specialist.preferences = prefs

            specialist.save(update_fields=["first_name", "last_name", "is_active", "preferences", "email"])
            messages.success(
                request,
                _("Atualização registrada para %(name)s.")
                % {"name": specialist.get_full_name()},
            )
            email = specialist.email
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

        try:
            start_date = datetime.strptime(self.request.GET.get("start_date", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            start_date = today - timedelta(days=29)

        try:
            end_date = datetime.strptime(self.request.GET.get("end_date", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            end_date = today

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        delta_days = (end_date - start_date).days
        previous_start = start_date - timedelta(days=delta_days + 1)
        previous_end = start_date - timedelta(days=1)

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
            stats["unique_patients"].add(response.patient_id or response.patient_display_name)

            if response.has_flags:
                stats["high_risk"] += 1

            response_date = response.created.date()
            if start_date <= response_date <= end_date:
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
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get("start_date", "")
        end_date = self.request.GET.get("end_date", "")
        municipality = self.request.GET.get("municipality", "")
        
        payload = _build_report_payload(start_date, end_date, municipality)

        # Get all municipalities
        all_cities = set()
        for resp in QuestionnaireResponse.objects.select_related("patient__parent__parent_profile"):
            city = _get_municipality(resp)
            if city and city != "-":
                all_cities.add(city)

        context.update(
            {
                "page_title": _("Relatorios Consolidados"),
                "start_date": payload["start_date"],
                "end_date": payload["end_date"],
                "selected_municipality": payload["municipality"],
                "all_municipalities": sorted(all_cities),
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
                "responses": payload["responses"],
            }
        )
        return context

class ReportsPdfExportView(AllowedRolesMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")
        municipality = request.GET.get("municipality", "")
        payload = _build_report_payload(start_date, end_date, municipality)

        context = {
            "payload": payload,
            "title": "Relatório de Distúrbios do Sono",
            "date": timezone.localtime().strftime("%d/%m/%Y %H:%M")
        }
        
        html_string = render_to_string("reports/pdf_template.html", context)
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorios-{payload["start_date"]}-{payload["end_date"]}.pdf"'
        )
        return response


class ReportsCsvExportView(AllowedRolesMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")
        municipality = request.GET.get("municipality", "")
        payload = _build_report_payload(start_date, end_date, municipality)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorios-{payload["start_date"]}-{payload["end_date"]}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["Período", f"{payload['start_date']} até {payload['end_date']}"])
        writer.writerow(["Município", payload["municipality"] or "Todos"])
        writer.writerow([])
        writer.writerow(["Métrica", "Valor"])
        for metric in payload["metrics"]:
            writer.writerow([metric["label"], metric["value"]])

        writer.writerow([])
        writer.writerow(["Avaliações"])
        writer.writerow([
            "Código", "Paciente", "Profissional", "Município", 
            "Pontuação", "Status", "Data"
        ])
        for r in payload["responses"]:
            status = _("Em revisão") if r.has_flags else _("Concluída")
            writer.writerow([
                r.pk,
                r.patient_display_name,
                _get_professional_name(r),
                _get_municipality(r),
                r.total_score,
                status,
                r.created.strftime("%Y-%m-%d")
            ])
            
        return response
