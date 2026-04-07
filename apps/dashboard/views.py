from collections import Counter
import csv
from urllib.parse import urlencode

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView
from django.views.generic import TemplateView

from apps.core.utils import generate_simple_pdf

RECENT_EVALUATIONS = [
    {
        "id": "EDSC-1001",
        "assessment_id": "4daee713-bf16-4f1f-b2eb-3ba8ff2d1ff1",
        "patient": "Ana Souza",
        "professional": "Dra. Camila Rocha",
        "municipality": "Recife",
        "status": "Concluida",
        "risk": "Moderado",
        "score": 38,
        "updated_at": "2026-04-02",
    },
    {
        "id": "EDSC-1002",
        "assessment_id": "feceb8c6-9cc8-44ea-8fdf-063387e9f6cf",
        "patient": "Marcos Lima",
        "professional": "Dr. Bruno Martins",
        "municipality": "Olinda",
        "status": "Em revisao",
        "risk": "Alto",
        "score": 58,
        "updated_at": "2026-04-03",
    },
    {
        "id": "EDSC-1003",
        "assessment_id": "2e1fed7d-9e6d-4ce3-a54d-708f6fb4baf6",
        "patient": "Juliana Alves",
        "professional": "Dra. Camila Rocha",
        "municipality": "Jaboatao",
        "status": "Concluida",
        "risk": "Baixo",
        "score": 21,
        "updated_at": "2026-04-03",
    },
    {
        "id": "EDSC-1004",
        "assessment_id": "8c7b5f4a-c36f-4a37-a469-fec7025f0d0a",
        "patient": "Priscila Gomes",
        "professional": "Dr. Felipe Moraes",
        "municipality": "Paulista",
        "status": "Pendente",
        "risk": "Moderado",
        "score": 0,
        "updated_at": "2026-04-04",
    },
    {
        "id": "EDSC-1005",
        "assessment_id": "9e9de89c-e96c-44bb-a765-6f39dbde5608",
        "patient": "Carlos Andrade",
        "professional": "Dr. Bruno Martins",
        "municipality": "Recife",
        "status": "Concluida",
        "risk": "Moderado",
        "score": 41,
        "updated_at": "2026-04-04",
    },
]

PROFESSIONALS = [
    {
        "name": "Dra. Camila Rocha",
        "email": "camila.rocha@sono.app.br",
        "role": "Psiquiatra",
        "status": "Ativo",
        "active_cases": 37,
        "municipality": "Recife",
    },
    {
        "name": "Dr. Bruno Martins",
        "email": "bruno.martins@sono.app.br",
        "role": "Psicologo",
        "status": "Ativo",
        "active_cases": 24,
        "municipality": "Olinda",
    },
    {
        "name": "Dr. Felipe Moraes",
        "email": "felipe.moraes@sono.app.br",
        "role": "Neurologista",
        "status": "Inativo",
        "active_cases": 0,
        "municipality": "Paulista",
    },
    {
        "name": "Dra. Luciana Costa",
        "email": "luciana.costa@sono.app.br",
        "role": "Enfermeira",
        "status": "Ativo",
        "active_cases": 12,
        "municipality": "Jaboatao",
    },
]

MUNICIPALITIES = [
    {
        "name": "Recife",
        "coverage": 82,
        "completed": 412,
        "high_risk": 68,
        "trend": "+9%",
    },
    {
        "name": "Olinda",
        "coverage": 73,
        "completed": 258,
        "high_risk": 43,
        "trend": "+5%",
    },
    {
        "name": "Jaboatao",
        "coverage": 69,
        "completed": 231,
        "high_risk": 51,
        "trend": "+4%",
    },
    {
        "name": "Paulista",
        "coverage": 61,
        "completed": 142,
        "high_risk": 29,
        "trend": "+2%",
    },
]

REPORT_SERIES = {
    "7d": {
        "bar": [
            {"label": "Seg", "value": 22},
            {"label": "Ter", "value": 25},
            {"label": "Qua", "value": 19},
            {"label": "Qui", "value": 31},
            {"label": "Sex", "value": 27},
            {"label": "Sab", "value": 14},
            {"label": "Dom", "value": 11},
        ],
        "line": [
            {"label": "Seg", "value": 38},
            {"label": "Ter", "value": 40},
            {"label": "Qua", "value": 37},
            {"label": "Qui", "value": 42},
            {"label": "Sex", "value": 41},
            {"label": "Sab", "value": 36},
            {"label": "Dom", "value": 35},
        ],
    },
    "30d": {
        "bar": [
            {"label": "Sem 1", "value": 121},
            {"label": "Sem 2", "value": 134},
            {"label": "Sem 3", "value": 129},
            {"label": "Sem 4", "value": 141},
        ],
        "line": [
            {"label": "Sem 1", "value": 37},
            {"label": "Sem 2", "value": 39},
            {"label": "Sem 3", "value": 38},
            {"label": "Sem 4", "value": 40},
        ],
    },
    "90d": {
        "bar": [
            {"label": "Jan", "value": 447},
            {"label": "Fev", "value": 462},
            {"label": "Mar", "value": 489},
        ],
        "line": [
            {"label": "Jan", "value": 36},
            {"label": "Fev", "value": 38},
            {"label": "Mar", "value": 39},
        ],
    },
}

PERIOD_LABELS = {
    "7d": _("Ultimos 7 dias"),
    "30d": _("Ultimos 30 dias"),
    "90d": _("Ultimos 90 dias"),
}


def _matches_filter(value: str, expected: str) -> bool:
    if not expected:
        return True
    return expected.lower() in value.lower()


def _filter_evaluations(
    patient: str,
    professional: str,
    status: str,
    risk: str,
) -> list[dict]:
    return [
        item
        for item in RECENT_EVALUATIONS
        if _matches_filter(item["patient"], patient)
        and _matches_filter(item["professional"], professional)
        and _matches_filter(item["status"], status)
        and _matches_filter(item["risk"], risk)
    ]


def _resolve_period(selected_period: str) -> str:
    return selected_period if selected_period in REPORT_SERIES else "30d"


def _build_report_metrics() -> list[dict]:
    return [
        {"label": _("Avaliacoes consolidadas"), "value": "2.194"},
        {"label": _("Risco alto"), "value": "17%"},
        {"label": _("Tempo medio de conclusao"), "value": "13 min"},
        {"label": _("Taxa de cobertura"), "value": "74%"},
    ]


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
    role = forms.CharField(
        label=_("Cargo"),
        max_length=120,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full"}),
    )
    municipality = forms.CharField(
        label=_("Municipio"),
        max_length=120,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full"}),
    )


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        risk_counter = Counter(item["risk"] for item in RECENT_EVALUATIONS)
        status_counter = Counter(item["status"] for item in RECENT_EVALUATIONS)
        context.update(
            {
                "page_title": _("Dashboard"),
                "dashboard_period": _("Ultimos 30 dias"),
                "kpi_cards": [
                    {
                        "label": _("Avaliacoes no periodo"),
                        "value": "1.247",
                        "trend": "+12%",
                        "trend_positive": True,
                    },
                    {
                        "label": _("Risco alto identificado"),
                        "value": str(risk_counter.get("Alto", 0)),
                        "trend": "-3%",
                        "trend_positive": False,
                    },
                    {
                        "label": _("Concluidas"),
                        "value": str(status_counter.get("Concluida", 0)),
                        "trend": "+8%",
                        "trend_positive": True,
                    },
                    {
                        "label": _("Profissionais ativos"),
                        "value": str(sum(item["status"] == "Ativo" for item in PROFESSIONALS)),
                        "trend": "+2",
                        "trend_positive": True,
                    },
                ],
                "recent_evaluations": RECENT_EVALUATIONS,
            }
        )
        return context


class EvaluationsListView(LoginRequiredMixin, TemplateView):
    template_name = "evaluations/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.GET.get("patient", "")
        professional = self.request.GET.get("professional", "")
        status = self.request.GET.get("status", "")
        risk = self.request.GET.get("risk", "")

        filtered = _filter_evaluations(
            patient=patient,
            professional=professional,
            status=status,
            risk=risk,
        )

        context.update(
            {
                "page_title": _("Gestao de Avaliacoes"),
                "evaluations": filtered,
                "applied_filters": {
                    "patient": patient,
                    "professional": professional,
                    "status": status,
                    "risk": risk,
                },
                "status_options": sorted({item["status"] for item in RECENT_EVALUATIONS}),
                "risk_options": sorted({item["risk"] for item in RECENT_EVALUATIONS}),
            }
        )
        return context


class ProfessionalsListView(LoginRequiredMixin, TemplateView):
    template_name = "professionals/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query", "")
        role = self.request.GET.get("role", "")
        status = self.request.GET.get("status", "")

        filtered = [
            item
            for item in PROFESSIONALS
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
                "page_title": _("Gestao de Profissionais"),
                "professionals": filtered,
                "applied_filters": {"query": query, "role": role, "status": status},
                "role_options": sorted({item["role"] for item in PROFESSIONALS}),
                "status_options": sorted({item["status"] for item in PROFESSIONALS}),
            }
        )
        return context


class ProfessionalManageView(LoginRequiredMixin, TemplateView):
    template_name = "professionals/manage.html"

    def _get_selected_email(self) -> str:
        return self.request.GET.get("email", "").strip()

    def _find_professional(self, email: str) -> dict | None:
        normalized_email = email.lower()
        for item in PROFESSIONALS:
            if item["email"].lower() == normalized_email:
                return item
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_email = self._get_selected_email()
        professional = self._find_professional(selected_email) if selected_email else None

        context.update(
            {
                "page_title": _("Gerenciar profissional"),
                "selected_email": selected_email,
                "professional": professional,
                "professional_not_found": selected_email and professional is None,
                "status_options": ["Ativo", "Inativo"],
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        professional = self._find_professional(email) if email else None

        if professional:
            messages.success(
                request,
                _(
                    "Dados recebidos para %(name)s. Persistencia de alteracoes sera habilitada na proxima etapa."
                )
                % {"name": professional["name"]},
            )
        else:
            messages.warning(
                request,
                _("Nao foi possivel identificar o profissional selecionado."),
            )

        params = urlencode({"email": email}) if email else ""
        target = reverse("dashboard:manage_professional")
        return redirect(f"{target}?{params}" if params else target)


class InviteProfessionalView(LoginRequiredMixin, FormView):
    template_name = "professionals/invite.html"
    form_class = InviteProfessionalForm
    success_url = reverse_lazy("dashboard:professionals")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Convidar profissional")
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            _("Convite enviado para %(email)s.") % {"email": form.cleaned_data["email"]},
        )
        return super().form_valid(form)


class MunicipalitiesView(LoginRequiredMixin, TemplateView):
    template_name = "municipalities/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query", "")

        ranking = [
            item
            for item in sorted(MUNICIPALITIES, key=lambda current: current["coverage"], reverse=True)
            if _matches_filter(item["name"], query)
        ]
        coverage_average = round(
            sum(item["coverage"] for item in MUNICIPALITIES) / len(MUNICIPALITIES),
            1,
        )

        context.update(
            {
                "page_title": _("Desempenho por Municipio"),
                "municipalities": ranking,
                "query": query,
                "coverage_average": coverage_average,
                "highlights": [
                    {
                        "label": _("Cobertura media"),
                        "value": f"{coverage_average}%",
                    },
                    {
                        "label": _("Municipio lider"),
                        "value": ranking[0]["name"] if ranking else "-",
                    },
                    {
                        "label": _("Avaliacoes concluidas"),
                        "value": str(sum(item["completed"] for item in MUNICIPALITIES)),
                    },
                ],
            }
        )
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "reports/index.html"

    PERIOD_OPTIONS = [
        ("7d", _("Ultimos 7 dias")),
        ("30d", _("Ultimos 30 dias")),
        ("90d", _("Ultimos 90 dias")),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_period = _resolve_period(self.request.GET.get("period", "30d"))

        bar_series = REPORT_SERIES[selected_period]["bar"]
        line_series = REPORT_SERIES[selected_period]["line"]

        context.update(
            {
                "page_title": _("Relatorios Consolidados"),
                "selected_period": selected_period,
                "period_options": self.PERIOD_OPTIONS,
                "metrics": _build_report_metrics(),
                "bar_series": bar_series,
                "line_series": line_series,
                "bar_max": max(item["value"] for item in bar_series),
                "line_max": max(item["value"] for item in line_series),
            }
        )
        return context


class EvaluationsCsvExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        filtered = _filter_evaluations(
            patient=request.GET.get("patient", ""),
            professional=request.GET.get("professional", ""),
            status=request.GET.get("status", ""),
            risk=request.GET.get("risk", ""),
        )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="avaliacoes.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "codigo",
                "paciente",
                "profissional",
                "municipio",
                "score",
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


class ReportsPdfExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        selected_period = _resolve_period(request.GET.get("period", "30d"))
        bar_series = REPORT_SERIES[selected_period]["bar"]
        line_series = REPORT_SERIES[selected_period]["line"]
        metrics = _build_report_metrics()

        lines = [f"Periodo: {PERIOD_LABELS[selected_period]}", "", "Metricas:"]
        for metric in metrics:
            lines.append(f"- {metric['label']}: {metric['value']}")

        lines.extend(["", "Volume de avaliacoes:"])
        for point in bar_series:
            lines.append(f"- {point['label']}: {point['value']}")

        lines.extend(["", "Media de score clinico:"])
        for point in line_series:
            lines.append(f"- {point['label']}: {point['value']}")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorios-{selected_period}.pdf"'
        )
        response.write(generate_simple_pdf("Relatorios consolidados", lines))
        return response


class ReportsCsvExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        selected_period = _resolve_period(request.GET.get("period", "30d"))
        bar_series = REPORT_SERIES[selected_period]["bar"]
        line_series = REPORT_SERIES[selected_period]["line"]
        metrics = _build_report_metrics()

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="relatorios-{selected_period}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["periodo", PERIOD_LABELS[selected_period]])
        writer.writerow([])
        writer.writerow(["metrica", "valor"])
        for metric in metrics:
            writer.writerow([metric["label"], metric["value"]])

        writer.writerow([])
        writer.writerow(["serie", "periodo", "valor"])
        for point in bar_series:
            writer.writerow(["volume_avaliacoes", point["label"], point["value"]])
        for point in line_series:
            writer.writerow(["media_score_clinico", point["label"], point["value"]])
        return response
