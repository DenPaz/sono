from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.assessments import constants
from apps.assessments.forms.professionals import ProfessionalInviteForm
from apps.assessments.selectors.professionals import get_professionals_table_data
from apps.assessments.selectors.professionals import get_recent_invites
from apps.assessments.views.mixins import AssessmentsCapabilityMixin


class ProfessionalsIndexView(AssessmentsCapabilityMixin, TemplateView):
    template_name = "assessments/professionals/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["professionals"] = get_professionals_table_data(
            user=self.request.user,
            capabilities=self.assessment_capabilities,
        )
        context["recent_invites"] = get_recent_invites(
            user=self.request.user,
            capabilities=self.assessment_capabilities,
        )
        context["invite_form"] = ProfessionalInviteForm()
        context["can_invite_professional"] = self.assessment_capabilities.get(
            constants.CAPABILITY_INVITE_PROFESSIONAL,
            False,
        )
        context["page_title"] = _("Profissionais")
        return context


class ProfessionalInviteCreateView(AssessmentsCapabilityMixin, View):
    required_capability = constants.CAPABILITY_INVITE_PROFESSIONAL

    def post(self, request, *args, **kwargs):
        form = ProfessionalInviteForm(data=request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.invited_by = request.user
            invite.save()
            messages.success(request, _("Convite enviado com sucesso."))
            form = ProfessionalInviteForm()
            status_code = 200
        else:
            messages.error(request, _("Não foi possível enviar o convite."))
            status_code = 422

        return render(
            request=request,
            template_name="assessments/professionals/partials/invite_modal.html",
            context={"invite_form": form},
            status=status_code,
        )
