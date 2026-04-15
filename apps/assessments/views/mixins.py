from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _

from apps.assessments.services.capabilities import get_assessment_capabilities


class FilterFormMixin:
    filter_form_class = None

    def get_filter_form_kwargs(self, *, request, capabilities) -> dict:
        return {}

    def build_filter_context(self, *, request, capabilities):
        if self.filter_form_class is None:
            msg = f"{self.__class__.__name__} must define filter_form_class."
            raise ImproperlyConfigured(msg)

        form = self.filter_form_class(
            data=request.GET or None,
            user=request.user,
            capabilities=capabilities,
            **self.get_filter_form_kwargs(
                request=request,
                capabilities=capabilities,
            ),
        )
        data = form.cleaned_data if form.is_valid() else {}
        return form, data


class AssessmentsCapabilityMixin:
    required_capability: str | None = None

    def get_assessment_capabilities(self) -> dict[str, bool]:
        return get_assessment_capabilities(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        self.assessment_capabilities = self.get_assessment_capabilities()
        has_required_capability = self.assessment_capabilities.get(
            self.required_capability,
            False,
        )
        if self.required_capability and not has_required_capability:
            return HttpResponseForbidden(_("Você não possui permissão para esta área."))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assessment_capabilities"] = getattr(
            self,
            "assessment_capabilities",
            self.get_assessment_capabilities(),
        )
        return context
