from django.urls import path

from .forms import QUESTIONNAIRE_FORMS
from .views import QuestionnaireWizardView

app_name = "patients"

urlpatterns = [
    path(
        route="<uuid:patient_pk>/questionnaire/",
        view=QuestionnaireWizardView.as_view(QUESTIONNAIRE_FORMS),
        name="questionnaire",
    ),
]
