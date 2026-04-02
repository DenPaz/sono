from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    """Form for user modification in the admin area."""

    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": forms.EmailField}


class UserAdminCreationForm(forms.ModelForm):
    """Form for user creation in the admin area."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }

    def save(self, *, commit=True):
        user = super().save(commit=False)
        user.password = make_password(None)
        if commit:
            user.save()
        return user
