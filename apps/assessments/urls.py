from django.urls import path

from apps.assessments.views.evaluations import EvaluationsIndexView
from apps.assessments.views.municipalities import MunicipalitiesIndexView
from apps.assessments.views.overview import OverviewIndexView
from apps.assessments.views.partials.evaluations import EvaluationsTablePartialView
from apps.assessments.views.partials.municipalities import (
    MunicipalitiesRankingPartialView,
)
from apps.assessments.views.partials.questionnaire import QuestionnaireStepPartialView
from apps.assessments.views.partials.reports import ReportsChartsPartialView
from apps.assessments.views.professionals import ProfessionalInviteCreateView
from apps.assessments.views.professionals import ProfessionalsIndexView
from apps.assessments.views.questionnaire import EvaluationCreateOrResumeView
from apps.assessments.views.questionnaire import EvaluationDetailView
from apps.assessments.views.reports import ReportsIndexView
from apps.assessments.views.settings import SettingsAccessView
from apps.assessments.views.settings import SettingsAccountView
from apps.assessments.views.settings import SettingsIndexView
from apps.assessments.views.settings import SettingsProfessionalActionView
from apps.assessments.views.settings import SettingsProfessionalsView

app_name = "assessments"

urlpatterns = [
    path("visao-geral/", OverviewIndexView.as_view(), name="overview"),
    path("avaliacoes/", EvaluationsIndexView.as_view(), name="evaluations"),
    path(
        "avaliacoes/nova/",
        EvaluationCreateOrResumeView.as_view(),
        name="evaluation_new",
    ),
    path(
        "avaliacoes/<uuid:evaluation_id>/",
        EvaluationDetailView.as_view(),
        name="evaluation_detail",
    ),
    path("profissionais/", ProfessionalsIndexView.as_view(), name="professionals"),
    path(
        "profissionais/convidar/",
        ProfessionalInviteCreateView.as_view(),
        name="professional_invite",
    ),
    path("municipios/", MunicipalitiesIndexView.as_view(), name="municipalities"),
    path("relatorios/", ReportsIndexView.as_view(), name="reports"),
    path("configuracoes/", SettingsIndexView.as_view(), name="settings"),
    path(
        "configuracoes/acessos/",
        SettingsAccessView.as_view(),
        name="settings_access",
    ),
    path(
        "configuracoes/conta/",
        SettingsAccountView.as_view(),
        name="settings_account",
    ),
    path(
        "configuracoes/profissionais/",
        SettingsProfessionalsView.as_view(),
        name="settings_professionals",
    ),
    path(
        "configuracoes/profissionais/acoes/",
        SettingsProfessionalActionView.as_view(),
        name="settings_professionals_action",
    ),
    path(
        "avaliacoes/partials/tabela/",
        EvaluationsTablePartialView.as_view(),
        name="evaluations_table_partial",
    ),
    path(
        "municipios/partials/ranking/",
        MunicipalitiesRankingPartialView.as_view(),
        name="municipalities_ranking_partial",
    ),
    path(
        "relatorios/partials/graficos/",
        ReportsChartsPartialView.as_view(),
        name="reports_charts_partial",
    ),
    path(
        "questionario/partials/passo/<int:step>/",
        QuestionnaireStepPartialView.as_view(),
        name="questionnaire_step_partial",
    ),
]
