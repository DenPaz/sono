from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth.hashers import make_password

from .models import Admin
from .models import Parent
from .models import Specialist
from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        ]


class UserAdminCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
        ]

    def save(self, *, commit=True):
        user = super().save(commit=False)
        user.password = make_password(None)
        if commit:
            user.save()
        return user


class AdminAdminChangeForm(UserAdminChangeForm):
    class Meta:
        model = Admin
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]


class AdminAdminCreationForm(UserAdminCreationForm):
    class Meta(UserAdminCreationForm.Meta):
        model = Admin
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class SpecialistAdminChangeForm(UserAdminChangeForm):
    class Meta:
        model = Specialist
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]


class SpecialistAdminCreationForm(UserAdminCreationForm):
    class Meta(UserAdminCreationForm.Meta):
        model = Specialist
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class ParentAdminChangeForm(UserAdminChangeForm):
    class Meta:
        model = Parent
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]


class ParentAdminCreationForm(UserAdminCreationForm):
    class Meta(UserAdminCreationForm.Meta):
        model = Parent
        fields = [
            "first_name",
            "last_name",
            "email",
        ]
