from django.views.generic import TemplateView

from apps.users.enums import UserRole


class IndexView(TemplateView):
    template_name = "dashboard/index.html"

    def get_template_names(self):
        role = self.request.user.role
        template_name = {
            UserRole.ADMIN: "dashboard/admin.html",
            UserRole.SPECIALIST: "dashboard/specialist.html",
            UserRole.PARENT: "dashboard/parent.html",
        }.get(role, self.template_name)
        return [template_name]
