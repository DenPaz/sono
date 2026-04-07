from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView


class SettingsView(LoginRequiredMixin, TemplateView):
	template_name = "users/settings/index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(
			{
				"page_title": _("Configuracoes"),
				"profile_data": {
					"first_name": self.request.user.first_name,
					"last_name": self.request.user.last_name,
					"email": self.request.user.email,
				},
				"preferences": {
					"email_alerts": True,
					"weekly_report": True,
					"lgpd_data_export": True,
				},
				"security": {
					"two_factor_enabled": False,
					"last_password_change": "2026-03-21",
				},
			}
		)
		return context

	def post(self, request, *args, **kwargs):
		messages.success(
			request,
			_("Configuracoes recebidas com sucesso. Integracao de persistencia sera aplicada na proxima etapa."),
		)
		return redirect("users:settings")
