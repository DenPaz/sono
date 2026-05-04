from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.i18n import set_language
from django_filters.views import FilterView

from apps.core.viewmixins import AllowedRolesMixin
from apps.core.viewmixins import HtmxTemplateMixin

from .enums import UserRole
from .filters import UserFilter
from .forms import AdminMultiModelCreateForm
from .forms import AdminMultiModelUpdateForm
from .models import Admin
from .models import Parent
from .models import User


# ---------------------------------------------------------------------------
# Utility views
# ---------------------------------------------------------------------------
class SetLanguageView(View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get("language")
        if language and hasattr(request.user, "profile"):
            profile = request.user.profile
            profile.language = language
            profile.save(update_fields=["language", "modified"])
        return set_language(request)


# ---------------------------------------------------------------------------
# User views
# ---------------------------------------------------------------------------
class UserListView(AllowedRolesMixin, HtmxTemplateMixin, FilterView):
    model = User
    filterset_class = UserFilter
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/user_list.html"
    htmx_template_name = "#user-table"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().with_profile()


# ---------------------------------------------------------------------------
# Admin views
# ---------------------------------------------------------------------------
class AdminCreateView(AllowedRolesMixin, SuccessMessageMixin, CreateView):
    model = Admin
    form_class = AdminMultiModelCreateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/admin_create.html"
    success_url = reverse_lazy("users:user_list")
    success_message = _("Admin created successfully.")


class AdminUpdateView(AllowedRolesMixin, SuccessMessageMixin, UpdateView):
    model = Admin
    form_class = AdminMultiModelUpdateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/admin_update.html"
    success_url = reverse_lazy("users:user_list")
    success_message = _("Admin updated successfully.")

    def get_queryset(self):
        return super().get_queryset().with_profile()


# ---------------------------------------------------------------------------
# Parent views
# ---------------------------------------------------------------------------
class ParentListView(UserListView):
    model = Parent
    allowed_roles = [UserRole.ADMIN, UserRole.PARENT]
    template_name = "users/parent_list.html"
    htmx_template_name = "#parent-table"
    context_object_name = "parents"
