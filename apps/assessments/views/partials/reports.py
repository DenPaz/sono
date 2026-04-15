from django.shortcuts import render
from django.views import View

from apps.assessments.forms.filters import ReportFiltersForm
from apps.assessments.selectors.reports import get_report_context
from apps.assessments.services.capabilities import get_assessment_capabilities
from apps.assessments.views.mixins import FilterFormMixin


class ReportsChartsPartialView(FilterFormMixin, View):
    filter_form_class = ReportFiltersForm

    def get(self, request, *args, **kwargs):
        capabilities = get_assessment_capabilities(user=request.user)
        _, filter_data = self.build_filter_context(
            request=request,
            capabilities=capabilities,
        )
        context = get_report_context(
            user=request.user,
            capabilities=capabilities,
            filters=filter_data,
        )
        return render(
            request=request,
            template_name="assessments/reports/partials/charts.html",
            context=context,
        )
