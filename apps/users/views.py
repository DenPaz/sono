from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.i18n import set_language
from django_filters.views import FilterView

from apps.core.viewmixins import AllowedRolesMixin
from apps.core.viewmixins import HtmxTemplateMixin

from .enums import UserRole
from .filters import UserFilter
from .models import Parent
from .models import User


class SetLanguageView(View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get("language")
        if language and hasattr(request.user, "profile"):
            profile = request.user.profile
            profile.language = language
            profile.save(update_fields=["language", "modified"])
        return set_language(request)


class UserListView(AllowedRolesMixin, HtmxTemplateMixin, FilterView):
    model = User
    filterset_class = UserFilter
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/user_list.html"
    htmx_template_name = "#user-table"
    context_object_name = "users"
    extra_context = {"page_title": _("Users")}
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().with_profile()


class ParentListView(UserListView):
    model = Parent
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST]
    template_name = "users/parent_list.html"
    htmx_template_name = "#parent-table"
    context_object_name = "parents"
    extra_context = {"page_title": _("Parents")}
