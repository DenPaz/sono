from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.assessments.forms.filters import MunicipalityFiltersForm
from apps.assessments.selectors.municipalities import get_municipality_ranking
from apps.assessments.selectors.municipalities import get_municipality_trend
from apps.assessments.views.mixins import AssessmentsCapabilityMixin
from apps.assessments.views.mixins import FilterFormMixin


class MunicipalitiesIndexView(
    AssessmentsCapabilityMixin,
    FilterFormMixin,
    TemplateView,
):
    template_name = "assessments/municipalities/index.html"
    filter_form_class = MunicipalityFiltersForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form, filter_data = self.build_filter_context(
            request=self.request,
            capabilities=self.assessment_capabilities,
        )
        period = int(filter_data.get("period") or 6)
        municipality = filter_data.get("municipality")

        context["filter_form"] = filter_form
        context["ranking_rows"] = get_municipality_ranking(
            user=self.request.user,
            capabilities=self.assessment_capabilities,
            period_months=period,
            municipality_id=str(municipality.id) if municipality else None,
        )
        context["trend_rows"] = get_municipality_trend(
            user=self.request.user,
            capabilities=self.assessment_capabilities,
            period_months=period,
            municipality_id=str(municipality.id) if municipality else None,
        )
        context["page_title"] = _("Municípios")
        return context
