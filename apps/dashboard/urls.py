from django.urls import path

from .views import EvaluationsListView
from .views import EvaluationsCsvExportView
from .views import InviteProfessionalView
from .views import IndexView
from .views import MunicipalitiesView
from .views import ProfessionalManageView
from .views import ProfessionalsListView
from .views import ReportsCsvExportView
from .views import ReportsPdfExportView
from .views import ReportsView

app_name = "dashboard"

urlpatterns = [
    path(
        route="",
        view=IndexView.as_view(),
        name="index",
    ),
    path(
        route="evaluations/",
        view=EvaluationsListView.as_view(),
        name="evaluations",
    ),
    path(
        route="evaluations/export/csv/",
        view=EvaluationsCsvExportView.as_view(),
        name="evaluations_export_csv",
    ),
    path(
        route="professionals/",
        view=ProfessionalsListView.as_view(),
        name="professionals",
    ),
    path(
        route="professionals/manage/",
        view=ProfessionalManageView.as_view(),
        name="manage_professional",
    ),
    path(
        route="professionals/invite/",
        view=InviteProfessionalView.as_view(),
        name="invite_professional",
    ),
    path(
        route="municipalities/",
        view=MunicipalitiesView.as_view(),
        name="municipalities",
    ),
    path(
        route="reports/",
        view=ReportsView.as_view(),
        name="reports",
    ),
    path(
        route="reports/export/pdf/",
        view=ReportsPdfExportView.as_view(),
        name="reports_export_pdf",
    ),
    path(
        route="reports/export/csv/",
        view=ReportsCsvExportView.as_view(),
        name="reports_export_csv",
    ),
]
