from django.shortcuts import render
from django.views import View

from apps.assessments.forms.filters import MunicipalityFiltersForm
from apps.assessments.selectors.municipalities import get_municipality_ranking
from apps.assessments.services.capabilities import get_assessment_capabilities
from apps.assessments.views.mixins import FilterFormMixin


class MunicipalitiesRankingPartialView(FilterFormMixin, View):
    filter_form_class = MunicipalityFiltersForm

    def get(self, request, *args, **kwargs):
        capabilities = get_assessment_capabilities(user=request.user)
        _, filter_data = self.build_filter_context(
            request=request,
            capabilities=capabilities,
        )
        period = int(filter_data.get("period") or 6)
        municipality = filter_data.get("municipality")
        ranking_rows = get_municipality_ranking(
            user=request.user,
            capabilities=capabilities,
            period_months=period,
            municipality_id=str(municipality.id) if municipality else None,
        )
        return render(
            request=request,
            template_name="assessments/municipalities/partials/ranking.html",
            context={"ranking_rows": ranking_rows},
        )
