from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.assessments.forms.filters import ReportFiltersForm
from apps.assessments.selectors.reports import get_report_context
from apps.assessments.views.mixins import AssessmentsCapabilityMixin
from apps.assessments.views.mixins import FilterFormMixin


class ReportsIndexView(AssessmentsCapabilityMixin, FilterFormMixin, TemplateView):
    template_name = "assessments/reports/index.html"
    filter_form_class = ReportFiltersForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form, filter_data = self.build_filter_context(
            request=self.request,
            capabilities=self.assessment_capabilities,
        )

        context["filter_form"] = filter_form
        context.update(
            get_report_context(
                user=self.request.user,
                capabilities=self.assessment_capabilities,
                filters=filter_data,
            )
        )
        context["page_title"] = _("Relatórios")
        return context
