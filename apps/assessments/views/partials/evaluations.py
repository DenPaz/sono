from django.shortcuts import render
from django.views import View

from apps.assessments import constants
from apps.assessments.forms.filters import EvaluationsFilterForm
from apps.assessments.selectors.evaluations import get_evaluations_page
from apps.assessments.services.capabilities import get_assessment_capabilities
from apps.assessments.views.mixins import FilterFormMixin


class EvaluationsTablePartialView(FilterFormMixin, View):
    filter_form_class = EvaluationsFilterForm

    def get_filter_form_kwargs(self, *, request, capabilities) -> dict:
        return {
            "show_professional_filter": capabilities.get(
                constants.CAPABILITY_VIEW_ALL_ASSESSMENTS,
                False,
            )
        }

    def get(self, request, *args, **kwargs):
        capabilities = get_assessment_capabilities(user=request.user)
        _, filters = self.build_filter_context(
            request=request,
            capabilities=capabilities,
        )

        page_obj = get_evaluations_page(
            user=request.user,
            capabilities=capabilities,
            filters=filters,
            page_number=request.GET.get("page", 1),
            per_page=10,
        )
        return render(
            request=request,
            template_name="assessments/evaluations/partials/table.html",
            context={"page_obj": page_obj},
        )
