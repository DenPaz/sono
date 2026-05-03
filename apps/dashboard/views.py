from django.views.generic import TemplateView

from apps.users.enums import UserRole


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
        return {}

    def _specialist_context(self):
        return {}

    def _parent_context(self):
        return {}
