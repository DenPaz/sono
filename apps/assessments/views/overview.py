from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.assessments.selectors.overview import get_overview_context
from apps.assessments.views.mixins import AssessmentsCapabilityMixin


class OverviewIndexView(AssessmentsCapabilityMixin, TemplateView):
    template_name = "assessments/overview/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            get_overview_context(
                user=self.request.user,
                capabilities=self.assessment_capabilities,
            )
        )
        context["page_title"] = _("Visão Geral")
        return context
