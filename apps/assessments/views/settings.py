from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.assessments import constants
from apps.assessments.forms.settings import PROFESSIONAL_ACTION_DEACTIVATE
from apps.assessments.forms.settings import PROFESSIONAL_ACTION_GRANT_ADMIN
from apps.assessments.forms.settings import PROFESSIONAL_ACTION_REACTIVATE
from apps.assessments.forms.settings import PROFESSIONAL_ACTION_REMOVE_ADMIN
from apps.assessments.forms.settings import PROFESSIONAL_ACTION_REVOKE_ACCESS
from apps.assessments.forms.settings import AccountEmailUpdateForm
from apps.assessments.forms.settings import AccountPasswordUpdateForm
from apps.assessments.forms.settings import ProfessionalManagementActionForm
from apps.assessments.models import INVITE_STATUS_PENDING
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import Municipality
from apps.assessments.models import ProfessionalInvite
from apps.assessments.models import ProfessionalProfile
from apps.assessments.permissions import ensure_assessment_groups
from apps.assessments.views.mixins import AssessmentsCapabilityMixin


class BaseSettingsView(AssessmentsCapabilityMixin, TemplateView):
    settings_section = "overview"
    page_title = _("Configurações")

    def can_manage_access(self) -> bool:
        if self.request.user.is_superuser:
            return True
        return self.assessment_capabilities.get(
            constants.CAPABILITY_MANAGE_ACCESS,
            False,
        )

    @staticmethod
    def get_pending_invites_queryset():
        return ProfessionalInvite.objects.filter(status=INVITE_STATUS_PENDING)

    @classmethod
    def get_operational_snapshot(cls) -> dict[str, int]:
        return {
            "active_professionals": ProfessionalProfile.objects.active().count(),
            "active_municipalities": Municipality.objects.active().count(),
            "pending_invites": cls.get_pending_invites_queryset().count(),
            "evaluations_today": AssessmentEvaluation.objects.active()
            .filter(
                created__date=timezone.localdate(),
            )
            .count(),
        }

    def get_settings_links(self) -> list[dict[str, str]]:
        if self.can_manage_access():
            return [
                {
                    "section": "access",
                    "label": str(_("Acessos")),
                    "url": reverse("assessments:settings_access"),
                },
                {
                    "section": "professionals",
                    "label": str(_("Profissionais")),
                    "url": reverse("assessments:settings_professionals"),
                },
                {
                    "section": "account",
                    "label": str(_("Conta e segurança")),
                    "url": reverse("assessments:settings_account"),
                },
            ]

        return [
            {
                "section": "account",
                "label": str(_("Conta e segurança")),
                "url": reverse("assessments:settings_account"),
            }
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["settings_section"] = self.settings_section
        context["settings_links"] = self.get_settings_links()
        context["operational_snapshot"] = self.get_operational_snapshot()
        context["can_manage_access"] = self.can_manage_access()
        return context


class SettingsIndexView(BaseSettingsView):
    def get(self, request, *args, **kwargs):
        if self.can_manage_access():
            return redirect("assessments:settings_access")
        return redirect("assessments:settings_account")


class SettingsAccessView(BaseSettingsView):
    template_name = "assessments/settings/access.html"
    required_capability = constants.CAPABILITY_MANAGE_ACCESS
    settings_section = "access"
    page_title = _("Configurações de acesso")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pending_invites_qs = self.get_pending_invites_queryset()
        context["access_snapshot"] = {
            "chief_admins": ProfessionalProfile.objects.active()
            .filter(user__groups__name=constants.ROLE_CHIEF_ADMIN)
            .distinct()
            .count(),
            "professionals": ProfessionalProfile.objects.active()
            .filter(user__groups__name=constants.ROLE_PROFESSIONAL)
            .distinct()
            .count(),
            "pending_invites": pending_invites_qs.count(),
        }
        context["pending_invites"] = pending_invites_qs.select_related(
            "municipality", "invited_by"
        ).order_by("-created")[:8]
        return context


class SettingsAccountView(BaseSettingsView):
    template_name = "assessments/settings/account.html"
    settings_section = "account"
    page_title = _("Conta e segurança")

    def _default_account_forms(self):
        return {
            "email_form": AccountEmailUpdateForm(user=self.request.user),
            "password_form": AccountPasswordUpdateForm(user=self.request.user),
        }

    def _render_account_forms(self, *, status: int = 200, **kwargs):
        default_forms = self._default_account_forms()
        default_forms.update(kwargs)
        return self.render_to_response(
            self.get_context_data(**default_forms),
            status=status,
        )

    def _handle_email_update(self, request):
        email_form = AccountEmailUpdateForm(data=request.POST, user=request.user)
        if email_form.is_valid():
            email_form.save()
            messages.success(request, _("E-mail atualizado com sucesso."))
            return redirect("assessments:settings_account")

        return self._render_account_forms(
            email_form=email_form,
            status=422,
        )

    def _handle_password_update(self, request):
        password_form = AccountPasswordUpdateForm(
            user=request.user,
            data=request.POST,
        )
        if password_form.is_valid():
            updated_user = password_form.save()
            update_session_auth_hash(request, updated_user)
            messages.success(request, _("Senha atualizada com sucesso."))
            return redirect("assessments:settings_account")

        return self._render_account_forms(
            password_form=password_form,
            status=422,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        defaults = self._default_account_forms()
        for key, form in defaults.items():
            context.setdefault(key, form)
        return context

    def post(self, request, *args, **kwargs):
        action_handlers = {
            "update_email": self._handle_email_update,
            "update_password": self._handle_password_update,
        }
        action = request.POST.get("action")
        handler = action_handlers.get(action)
        if handler:
            return handler(request)

        messages.error(request, _("Ação de conta inválida."))
        return redirect("assessments:settings_account")


class SettingsProfessionalsView(BaseSettingsView):
    template_name = "assessments/settings/professionals.html"
    required_capability = constants.CAPABILITY_MANAGE_ACCESS
    settings_section = "professionals"
    page_title = _("Gestão de profissionais")

    @staticmethod
    def _get_role_label(*, group_names: set[str]) -> str:
        if constants.ROLE_CHIEF_ADMIN in group_names:
            return str(_("Chefe/Admin"))
        if constants.ROLE_PROFESSIONAL in group_names:
            return str(_("Profissional"))
        return str(_("Sem acesso operacional"))

    @staticmethod
    def _build_action(
        *,
        value: str,
        label: str,
        css_class: str,
    ) -> dict[str, str]:
        return {
            "value": value,
            "label": label,
            "css_class": css_class,
        }

    def _get_row_actions(
        self,
        *,
        is_chief_admin: bool,
        is_active: bool,
        is_self: bool,
    ) -> list[dict[str, str]]:
        actions = []
        if is_chief_admin:
            actions.append(
                self._build_action(
                    value=PROFESSIONAL_ACTION_REMOVE_ADMIN,
                    label=str(_("Remover admin")),
                    css_class="btn btn-outline btn-xs",
                )
            )
        else:
            actions.append(
                self._build_action(
                    value=PROFESSIONAL_ACTION_GRANT_ADMIN,
                    label=str(_("Conceder admin")),
                    css_class="btn btn-outline btn-xs",
                )
            )

        if not is_self:
            actions.append(
                self._build_action(
                    value=PROFESSIONAL_ACTION_REVOKE_ACCESS,
                    label=str(_("Revogar acesso")),
                    css_class="btn btn-warning btn-soft btn-xs",
                )
            )

            if is_active:
                actions.append(
                    self._build_action(
                        value=PROFESSIONAL_ACTION_DEACTIVATE,
                        label=str(_("Desativar")),
                        css_class="btn btn-error btn-soft btn-xs",
                    )
                )
            else:
                actions.append(
                    self._build_action(
                        value=PROFESSIONAL_ACTION_REACTIVATE,
                        label=str(_("Reativar")),
                        css_class="btn btn-success btn-soft btn-xs",
                    )
                )

        return actions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = (
            ProfessionalProfile.objects.select_related("user", "municipality")
            .prefetch_related("user__groups")
            .annotate(total_evaluations=Count("user__assessments", distinct=True))
            .order_by("user__first_name", "user__last_name")
        )

        rows = []
        for profile in profiles:
            group_names = {group.name for group in profile.user.groups.all()}
            is_chief_admin = constants.ROLE_CHIEF_ADMIN in group_names
            is_professional = constants.ROLE_PROFESSIONAL in group_names
            is_active = profile.is_active and profile.user.is_active
            rows.append(
                {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    "name": profile.user.get_full_name() or profile.user.email,
                    "email": profile.user.email,
                    "municipality": profile.municipality,
                    "is_active": is_active,
                    "role_label": self._get_role_label(group_names=group_names),
                    "is_chief_admin": is_chief_admin,
                    "is_professional": is_professional,
                    "total_evaluations": profile.total_evaluations,
                    "actions": self._get_row_actions(
                        is_chief_admin=is_chief_admin,
                        is_active=is_active,
                        is_self=profile.user_id == self.request.user.id,
                    ),
                }
            )

        context["managed_professionals"] = rows
        return context


class SettingsProfessionalActionView(AssessmentsCapabilityMixin, View):
    required_capability = constants.CAPABILITY_MANAGE_ACCESS

    @staticmethod
    def _redirect_to_professionals():
        return redirect("assessments:settings_professionals")

    def _notify_and_redirect(self, *, request, level: str, message: str):
        notifier = getattr(messages, level)
        notifier(request, message)
        return self._redirect_to_professionals()

    def _handle_grant_admin(
        self,
        *,
        request,
        profile: ProfessionalProfile,
        chief_admin_group: Group,
        professional_group: Group,
    ):
        profile.user.groups.add(chief_admin_group, professional_group)
        return self._notify_and_redirect(
            request=request,
            level="success",
            message=_("Permissão administrativa concedida com sucesso."),
        )

    def _handle_remove_admin(
        self,
        *,
        request,
        profile: ProfessionalProfile,
        chief_admin_group: Group,
        professional_group: Group,
    ):
        profile.user.groups.remove(chief_admin_group)
        profile.user.groups.add(professional_group)
        return self._notify_and_redirect(
            request=request,
            level="success",
            message=_("Permissão administrativa removida com sucesso."),
        )

    def _handle_revoke_access(
        self,
        *,
        request,
        profile: ProfessionalProfile,
        chief_admin_group: Group,
        professional_group: Group,
    ):
        profile.user.groups.remove(chief_admin_group, professional_group)
        return self._notify_and_redirect(
            request=request,
            level="success",
            message=_("Acesso operacional revogado com sucesso."),
        )

    def _handle_deactivate(
        self,
        *,
        request,
        profile: ProfessionalProfile,
        chief_admin_group: Group,
        professional_group: Group,
    ):
        profile.is_active = False
        profile.user.is_active = False
        profile.save(update_fields=["is_active", "modified"])
        profile.user.save(update_fields=["is_active", "modified"])
        return self._notify_and_redirect(
            request=request,
            level="success",
            message=_("Profissional desativado com sucesso."),
        )

    def _handle_reactivate(
        self,
        *,
        request,
        profile: ProfessionalProfile,
        chief_admin_group: Group,
        professional_group: Group,
    ):
        profile.is_active = True
        profile.user.is_active = True
        profile.save(update_fields=["is_active", "modified"])
        profile.user.save(update_fields=["is_active", "modified"])
        return self._notify_and_redirect(
            request=request,
            level="success",
            message=_("Profissional reativado com sucesso."),
        )

    def post(self, request, *args, **kwargs):
        form = ProfessionalManagementActionForm(data=request.POST)
        if not form.is_valid():
            return self._notify_and_redirect(
                request=request,
                level="error",
                message=_("Ação inválida para gestão de profissionais."),
            )

        profile = get_object_or_404(
            ProfessionalProfile.objects.select_related("user"),
            id=form.cleaned_data["profile_id"],
        )
        action = form.cleaned_data["action"]

        if profile.user_id == request.user.id and action in {
            PROFESSIONAL_ACTION_REMOVE_ADMIN,
            PROFESSIONAL_ACTION_REVOKE_ACCESS,
            PROFESSIONAL_ACTION_DEACTIVATE,
        }:
            messages.error(
                request,
                _("Não é permitido remover o seu próprio acesso administrativo."),
            )
            return self._redirect_to_professionals()

        ensure_assessment_groups()
        chief_admin_group = Group.objects.get_or_create(
            name=constants.ROLE_CHIEF_ADMIN
        )[0]
        professional_group = Group.objects.get_or_create(
            name=constants.ROLE_PROFESSIONAL
        )[0]

        action_handlers = {
            PROFESSIONAL_ACTION_GRANT_ADMIN: self._handle_grant_admin,
            PROFESSIONAL_ACTION_REMOVE_ADMIN: self._handle_remove_admin,
            PROFESSIONAL_ACTION_REVOKE_ACCESS: self._handle_revoke_access,
            PROFESSIONAL_ACTION_DEACTIVATE: self._handle_deactivate,
            PROFESSIONAL_ACTION_REACTIVATE: self._handle_reactivate,
        }
        handler = action_handlers.get(action)
        if not handler:
            return self._notify_and_redirect(
                request=request,
                level="error",
                message=_("Ação não suportada."),
            )

        return handler(
            request=request,
            profile=profile,
            chief_admin_group=chief_admin_group,
            professional_group=professional_group,
        )
