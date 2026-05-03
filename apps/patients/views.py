from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from formtools.wizard.views import SessionWizardView

from apps.core.viewmixins import AllowedRolesMixin
from apps.users.enums import UserRole

from .forms import QUESTIONNAIRE_FORMS
from .forms import STEP_TITLES
from .models import Patient
from .models import QuestionnaireResponse


class QuestionnaireWizardView(AllowedRolesMixin, SessionWizardView):
    template_name = "patients/questionnaire_wizard.html"
    form_list = QUESTIONNAIRE_FORMS
    allowed_roles = [UserRole.PARENT]

    def dispatch(self, request, *args, **kwargs):
        self.patient = get_object_or_404(
            Patient,
            pk=self.kwargs["patient_pk"],
            parent=request.user,
            is_active=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step = self.steps.current
        context.update(
            {
                "page_title": _("Sleep questionnaire"),
                "patient": self.patient,
                "step_titles_list": list(STEP_TITLES.values()),
                "current_step_title": STEP_TITLES.get(current_step, ""),
            }
        )
        return context

    def done(self, form_list, **kwargs):
        QuestionnaireResponse.objects.create(
            patient=self.patient,
            **self.get_all_cleaned_data(),
        )
        messages.success(self.request, _("Questionnaire submitted successfully."))
        return redirect(reverse_lazy("dashboard:index"))
