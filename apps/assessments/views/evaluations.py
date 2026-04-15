from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.assessments import constants
from apps.assessments.forms.filters import EvaluationsFilterForm
from apps.assessments.selectors.evaluations import get_evaluations_page
from apps.assessments.views.mixins import AssessmentsCapabilityMixin
from apps.assessments.views.mixins import FilterFormMixin


class EvaluationsIndexView(AssessmentsCapabilityMixin, FilterFormMixin, TemplateView):
    template_name = "assessments/evaluations/index.html"
    filter_form_class = EvaluationsFilterForm

    def get_filter_form_kwargs(self, *, request, capabilities) -> dict:
        return {
            "show_professional_filter": capabilities.get(
                constants.CAPABILITY_VIEW_ALL_ASSESSMENTS,
                False,
            )
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form, filter_data = self.build_filter_context(
            request=self.request,
            capabilities=self.assessment_capabilities,
        )

        page_obj = get_evaluations_page(
            user=self.request.user,
            capabilities=self.assessment_capabilities,
            filters=filter_data,
            page_number=self.request.GET.get("page", 1),
            per_page=10,
        )

        context["filter_form"] = filter_form
        context["page_obj"] = page_obj
        context["page_title"] = _("Avaliações")
        return context
