from django.urls import path

from .forms import QUESTIONNAIRE_FORMS
from .views import PatientCreateView
from .views import PatientDetailView
from .views import PatientListView
from .views import PatientUpdateView
from .views import QuestionnaireWizardView

app_name = "patients"

urlpatterns = [
    path("", PatientListView.as_view(), name="patient_list"),
    path("create/", PatientCreateView.as_view(), name="patient_create"),
    path("<uuid:pk>/", PatientDetailView.as_view(), name="patient_detail"),
    path("<uuid:pk>/update/", PatientUpdateView.as_view(), name="patient_update"),
    path(
        route="<uuid:patient_pk>/questionnaire/",
        view=QuestionnaireWizardView.as_view(QUESTIONNAIRE_FORMS),
        name="questionnaire",
    ),
]
