from django.views.generic import TemplateView

from apps.patients.models import Patient
from apps.patients.models import QuestionnaireResponse
from apps.users.enums import UserRole
from apps.users.models import Admin
from apps.users.models import Parent
from apps.users.models import Specialist


class IndexView(TemplateView):
    template_name = "dashboard/index.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.role = request.user.role

    def get_template_names(self):
        template_name = {
            UserRole.ADMIN: "dashboard/admin.html",
            UserRole.SPECIALIST: "dashboard/specialist.html",
            UserRole.PARENT: "dashboard/parent.html",
        }.get(self.role, self.template_name)
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handler = {
            UserRole.ADMIN: self._admin_context,
            UserRole.SPECIALIST: self._specialist_context,
            UserRole.PARENT: self._parent_context,
        }.get(self.role)
        if handler:
            context.update(handler())
        return context

    def _admin_context(self):
        recent_responses = QuestionnaireResponse.objects.select_related(
            "patient"
        ).order_by("-created")[:8]
        return {
            "stats": {
                "admins": Admin.objects.count(),
                "specialists": Specialist.objects.count(),
                "parents": Parent.objects.count(),
                "patients": Patient.objects.active().count(),
            },
            "recent_responses": recent_responses,
        }

    def _specialist_context(self):
        user = self.request.user
        recent_responses = (
            QuestionnaireResponse.objects.filter(patient__specialist=user)
            .select_related("patient")
            .order_by("-created")[:8]
        )
        return {
            "patient_count": Patient.objects.filter(
                specialist=user, is_active=True
            ).count(),
            "recent_responses": recent_responses,
        }

    def _parent_context(self):
        user = self.request.user
        patients = Patient.objects.filter(parent=user, is_active=True).prefetch_related(
            "questionnaire_responses"
        )
        recent_responses = (
            QuestionnaireResponse.objects.filter(patient__parent=user)
            .select_related("patient")
            .order_by("-created")[:5]
        )
        return {
            "patients": patients,
            "recent_responses": recent_responses,
        }
