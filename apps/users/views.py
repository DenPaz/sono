from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.i18n import set_language
from django_filters.views import FilterView

from apps.core.viewmixins import AllowedRolesMixin
from apps.core.viewmixins import HtmxFormSuccessMixin
from apps.core.viewmixins import HtmxTemplateMixin

from .enums import UserRole
from .filters import UserFilter
from .forms import AdminMultiModelCreateForm
from .forms import AdminMultiModelSelfUpdateForm
from .forms import AdminMultiModelUpdateForm
from .forms import ParentMultiModelCreateForm
from .forms import ParentMultiModelSelfUpdateForm
from .forms import ParentMultiModelUpdateForm
from .forms import SpecialistMultiModelCreateForm
from .forms import SpecialistMultiModelSelfUpdateForm
from .forms import SpecialistMultiModelUpdateForm
from .models import Admin
from .models import Parent
from .models import Specialist
from .models import User
from .viewmixins import SendInvitationEmailMixin


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
class AdminCreateView(
    SendInvitationEmailMixin,
    AllowedRolesMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Admin
    form_class = AdminMultiModelCreateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/admin_create.html"
    success_url = reverse_lazy("users:user_list")
    success_message = _("Admin created successfully.")


class AdminUpdateView(
    AllowedRolesMixin,
    HtmxTemplateMixin,
    HtmxFormSuccessMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Admin
    form_class = AdminMultiModelUpdateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/admin_update.html"
    htmx_template_name = "#update-form"
    success_url = reverse_lazy("users:user_list")
    success_message = _("Admin updated successfully.")

    def get_queryset(self):
        return super().get_queryset().with_profile()


# ---------------------------------------------------------------------------
# Specialist views
# ---------------------------------------------------------------------------
class SpecialistCreateView(
    SendInvitationEmailMixin,
    AllowedRolesMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Specialist
    form_class = SpecialistMultiModelCreateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/specialist_create.html"
    success_url = reverse_lazy("users:user_list")
    success_message = _("Specialist created successfully.")


class SpecialistUpdateView(
    AllowedRolesMixin,
    HtmxTemplateMixin,
    HtmxFormSuccessMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Specialist
    form_class = SpecialistMultiModelUpdateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/specialist_update.html"
    htmx_template_name = "#update-form"
    success_url = reverse_lazy("users:user_list")
    success_message = _("Specialist updated successfully.")

    def get_queryset(self):
        return super().get_queryset().with_profile()


# ---------------------------------------------------------------------------
# Parent views
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Profile view (self-service, any authenticated user)
# ---------------------------------------------------------------------------
class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")
    success_message = _("Profile updated successfully.")

    _proxy_models = {
        UserRole.ADMIN: Admin,
        UserRole.SPECIALIST: Specialist,
        UserRole.PARENT: Parent,
    }
    _self_update_forms = {
        UserRole.ADMIN: AdminMultiModelSelfUpdateForm,
        UserRole.SPECIALIST: SpecialistMultiModelSelfUpdateForm,
        UserRole.PARENT: ParentMultiModelSelfUpdateForm,
    }

    def get_object(self, queryset=None):
        proxy = self._proxy_models[self.request.user.role]
        return proxy.objects.with_profile().get(pk=self.request.user.pk)

    def get_form_class(self):
        return self._self_update_forms[self.request.user.role]


# ---------------------------------------------------------------------------
# Parent views
# ---------------------------------------------------------------------------
class ParentListView(UserListView):
    model = Parent
    allowed_roles = [UserRole.ADMIN, UserRole.PARENT]
    template_name = "users/parent_list.html"
    htmx_template_name = "#parent-table"
    context_object_name = "parents"


class ParentCreateView(
    SendInvitationEmailMixin,
    AllowedRolesMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Parent
    form_class = ParentMultiModelCreateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/parent_create.html"
    success_url = reverse_lazy("users:parent_list")
    success_message = _("Parent created successfully.")


class ParentUpdateView(
    AllowedRolesMixin,
    HtmxTemplateMixin,
    HtmxFormSuccessMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Parent
    form_class = ParentMultiModelUpdateForm
    allowed_roles = [UserRole.ADMIN]
    template_name = "users/parent_update.html"
    htmx_template_name = "#update-form"
    success_url = reverse_lazy("users:parent_list")
    success_message = _("Parent updated successfully.")

    def get_queryset(self):
        return super().get_queryset().with_profile()
