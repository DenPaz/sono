from __future__ import annotations

from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()

PROFESSIONAL_ACTION_GRANT_ADMIN = "grant_admin"
PROFESSIONAL_ACTION_REMOVE_ADMIN = "remove_admin"
PROFESSIONAL_ACTION_REVOKE_ACCESS = "revoke_access"
PROFESSIONAL_ACTION_DEACTIVATE = "deactivate"
PROFESSIONAL_ACTION_REACTIVATE = "reactivate"


class ProfessionalManagementActionForm(forms.Form):
    profile_id = forms.UUIDField()
    action = forms.ChoiceField(
        choices=(
            (PROFESSIONAL_ACTION_GRANT_ADMIN, _("Conceder perfil administrativo")),
            (PROFESSIONAL_ACTION_REMOVE_ADMIN, _("Remover perfil administrativo")),
            (PROFESSIONAL_ACTION_REVOKE_ACCESS, _("Revogar acesso operacional")),
            (PROFESSIONAL_ACTION_DEACTIVATE, _("Desativar profissional")),
            (PROFESSIONAL_ACTION_REACTIVATE, _("Reativar profissional")),
        ),
    )


class AccountEmailUpdateForm(forms.Form):
    email = forms.EmailField(label=_("Novo e-mail"))
    current_password = forms.CharField(
        label=_("Senha atual"),
        widget=forms.PasswordInput(),
    )

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields["email"].initial = user.email

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_("Senha atual inválida."))
        return current_password

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if (
            UserModel.objects.filter(email__iexact=email)
            .exclude(pk=self.user.pk)
            .exists()
        ):
            raise forms.ValidationError(_("Este e-mail já está em uso."))
        return email

    def save(self) -> None:
        email = self.cleaned_data["email"]
        self.user.email = email
        self.user.save(update_fields=["email", "modified"])

        EmailAddress.objects.filter(user=self.user).update(primary=False)
        EmailAddress.objects.update_or_create(
            user=self.user,
            email=email,
            defaults={"primary": True, "verified": False},
        )


class AccountPasswordUpdateForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Senha atual"),
        widget=forms.PasswordInput(),
    )
    new_password1 = forms.CharField(
        label=_("Nova senha"),
        widget=forms.PasswordInput(),
    )
    new_password2 = forms.CharField(
        label=_("Confirme a nova senha"),
        widget=forms.PasswordInput(),
    )
