from django.urls import path

from .views import AssessmentResultPdfExportView
from .views import AssessmentResultView
from .views import QuestionnaireWizardView

app_name = "assessments"

urlpatterns = [
    path(
        route="questionnaire/",
        view=QuestionnaireWizardView.as_view(),
        name="questionnaire",
    ),
    path(
        route="results/<uuid:assessment_id>/",
        view=AssessmentResultView.as_view(),
        name="results",
    ),
    path(
        route="results/<uuid:assessment_id>/export/pdf/",
        view=AssessmentResultPdfExportView.as_view(),
        name="results_export_pdf",
    ),
]
