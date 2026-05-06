from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import FormView
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
from .forms import UserSettingsForm
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
    success_message = _("Administrador criado com sucesso.")


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
    success_message = _("Administrador atualizado com sucesso.")

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
    success_message = _("Especialista criado com sucesso.")


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
    success_message = _("Especialista atualizado com sucesso.")

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
    success_message = _("Perfil atualizado com sucesso.")

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
# Settings view (admin only)
# ---------------------------------------------------------------------------
class SettingsView(AllowedRolesMixin, FormView):
    template_name = "users/settings/index.html"
    form_class = UserSettingsForm
    allowed_roles = [UserRole.ADMIN]
    success_url = reverse_lazy("users:settings")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_password_change = (
            timezone.localtime(self.request.user.password_changed_at).strftime(
                "%d/%m/%Y %H:%M"
            )
            if self.request.user.password_changed_at
            else "-"
        )
        context.update(
            {
                "page_title": _("Configurações"),
                "security": {
                    "two_factor_enabled": False,
                    "last_password_change": last_password_change,
                },
            }
        )
        return context

    def form_valid(self, form):
        user = form.save()
        if form.cleaned_data.get("new_password"):
            update_session_auth_hash(self.request, user)
        messages.success(
            self.request,
            _("Configurações atualizadas com sucesso."),
        )
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Parent views
# ---------------------------------------------------------------------------
class ParentListView(UserListView):
    model = Parent
    allowed_roles = [UserRole.ADMIN, UserRole.SPECIALIST]
    template_name = "users/parent_list.html"
    htmx_template_name = "#parent-table"
    context_object_name = "parents"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == UserRole.SPECIALIST:
            return queryset.filter(patients__specialist=self.request.user).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Responsáveis")
        return context


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
    success_message = _("Responsável criado com sucesso.")


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
    success_message = _("Responsável atualizado com sucesso.")

    def get_queryset(self):
        return super().get_queryset().with_profile()
