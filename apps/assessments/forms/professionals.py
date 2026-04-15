from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.assessments.models import Municipality
from apps.assessments.models import ProfessionalInvite

User = get_user_model()


class ProfessionalInviteForm(forms.ModelForm):
    class Meta:
        model = ProfessionalInvite
        fields = ["first_name", "last_name", "email", "municipality"]
        labels = {
            "first_name": _("Nome"),
            "last_name": _("Sobrenome"),
            "email": _("Email"),
            "municipality": _("Município"),
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "input w-full"}),
            "last_name": forms.TextInput(attrs={"class": "input w-full"}),
            "email": forms.EmailInput(attrs={"class": "input w-full"}),
            "municipality": forms.Select(attrs={"class": "select w-full"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["municipality"].queryset = Municipality.objects.active()

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            msg = _("Já existe um usuário ativo com este email.")
            raise forms.ValidationError(msg)
        return email
