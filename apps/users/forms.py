from betterforms.multiform import MultiModelForm
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import DEFAULT_USER_PREFERENCES
from .models import Admin
from .models import AdminProfile
from .models import Parent
from .models import ParentProfile
from .models import Specialist
from .models import SpecialistProfile
from .models import User


# ---------------------------------------------------------------------------
# Base forms
# ---------------------------------------------------------------------------
class UserCreateForm(forms.ModelForm):
    class Meta:
        fields = ["first_name", "last_name", "email"]

    def save(self, commit=True):  # noqa: FBT002
        user = super().save(commit=False)
        user.password = make_password(None)
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        fields = ["first_name", "last_name", "email", "is_active"]


class UserSelfUpdateForm(forms.ModelForm):
    class Meta:
        fields = ["first_name", "last_name", "email"]


class UserProfileCreateForm(forms.ModelForm):
    class Meta:
        fields = ["avatar"]


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        fields = ["avatar", "language"]


# ---------------------------------------------------------------------------
# Base MultiModelForms
# ---------------------------------------------------------------------------
class UserMultiModelCreateForm(MultiModelForm):
    """Base create form for all user roles.

    Saves the user first (triggering the post_save signal that creates the
    profile), then binds the signal-created profile instance to the profile
    child form and saves it. Subclasses only need to declare `form_classes`
    and the `profile_related_name` for their role.
    """

    profile_related_name = None

    def save(self, commit=True):  # noqa: FBT002
        user = self.forms["user"].save(commit=commit)
        if commit:
            profile_form = self.forms["profile"]
            profile_form.instance = getattr(user, self.profile_related_name)
            profile_form.save()
        return user


class UserMultiModelUpdateForm(MultiModelForm):
    """Base update form for all user roles.

    Intercepts the single model instance passed by UpdateView and splits it
    into the dict betterforms expects. Subclasses only need to declare
    `form_classes` and the `profile_related_name` for their role.
    """

    profile_related_name = None

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        if instance is not None:
            kwargs["instance"] = {
                "user": instance,
                "profile": getattr(instance, self.profile_related_name),
            }
        super().__init__(*args, **kwargs)


# ---------------------------------------------------------------------------
# Admin forms
# ---------------------------------------------------------------------------
class AdminCreateForm(UserCreateForm):
    class Meta(UserCreateForm.Meta):
        model = Admin


class AdminUpdateForm(UserUpdateForm):
    class Meta(UserUpdateForm.Meta):
        model = Admin


class AdminProfileCreateForm(UserProfileCreateForm):
    class Meta(UserProfileCreateForm.Meta):
        model = AdminProfile


class AdminProfileUpdateForm(UserProfileUpdateForm):
    class Meta(UserProfileUpdateForm.Meta):
        model = AdminProfile


class AdminMultiModelCreateForm(UserMultiModelCreateForm):
    profile_related_name = "admin_profile"
    form_classes = {
        "user": AdminCreateForm,
        "profile": AdminProfileCreateForm,
    }


class AdminMultiModelUpdateForm(UserMultiModelUpdateForm):
    profile_related_name = "admin_profile"
    form_classes = {
        "user": AdminUpdateForm,
        "profile": AdminProfileUpdateForm,
    }


# ---------------------------------------------------------------------------
# Specialist forms
# ---------------------------------------------------------------------------
class SpecialistCreateForm(UserCreateForm):
    class Meta(UserCreateForm.Meta):
        model = Specialist


class SpecialistUpdateForm(UserUpdateForm):
    class Meta(UserUpdateForm.Meta):
        model = Specialist


class SpecialistProfileCreateForm(UserProfileCreateForm):
    class Meta(UserProfileCreateForm.Meta):
        model = SpecialistProfile


class SpecialistProfileUpdateForm(UserProfileUpdateForm):
    class Meta(UserProfileUpdateForm.Meta):
        model = SpecialistProfile


class SpecialistMultiModelCreateForm(UserMultiModelCreateForm):
    profile_related_name = "specialist_profile"
    form_classes = {
        "user": SpecialistCreateForm,
        "profile": SpecialistProfileCreateForm,
    }


class SpecialistMultiModelUpdateForm(UserMultiModelUpdateForm):
    profile_related_name = "specialist_profile"
    form_classes = {
        "user": SpecialistUpdateForm,
        "profile": SpecialistProfileUpdateForm,
    }


# ---------------------------------------------------------------------------
# Parent forms
# ---------------------------------------------------------------------------
class ParentCreateForm(UserCreateForm):
    patients = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        label=_("Associar dependentes existentes"),
        help_text=_("Selecione pacientes que já existem mas precisam ser vinculados a este responsável."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.patients.models import Patient
        self.fields["patients"].queryset = Patient.objects.all()

    class Meta(UserCreateForm.Meta):
        model = Parent

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            for patient in self.cleaned_data.get("patients", []):
                patient.parent = user
                patient.save()
        return user


class ParentUpdateForm(UserUpdateForm):
    patients = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        label=_("Associar dependentes existentes"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.patients.models import Patient
        self.fields["patients"].queryset = Patient.objects.all()
        if self.instance.pk:
            self.fields["patients"].initial = self.instance.patients.all()

    class Meta(UserUpdateForm.Meta):
        model = Parent

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            for patient in self.cleaned_data.get("patients", []):
                patient.parent = user
                patient.save()
        return user


class ParentProfileCreateForm(UserProfileCreateForm):
    class Meta(UserProfileCreateForm.Meta):
        model = ParentProfile
        fields = [
            *UserProfileCreateForm.Meta.fields,
            "phone",
            "birth_date",
        ]


class ParentProfileUpdateForm(UserProfileUpdateForm):
    class Meta(UserProfileUpdateForm.Meta):
        model = ParentProfile
        fields = [
            *UserProfileUpdateForm.Meta.fields,
            "phone",
            "birth_date",
            "address",
        ]


class ParentMultiModelCreateForm(UserMultiModelCreateForm):
    profile_related_name = "parent_profile"
    form_classes = {
        "user": ParentCreateForm,
        "profile": ParentProfileCreateForm,
    }


class ParentMultiModelUpdateForm(UserMultiModelUpdateForm):
    profile_related_name = "parent_profile"
    form_classes = {
        "user": ParentUpdateForm,
        "profile": ParentProfileUpdateForm,
    }


# ---------------------------------------------------------------------------
# Self-update forms (no is_active — users cannot deactivate themselves)
# ---------------------------------------------------------------------------
class AdminSelfUpdateForm(UserSelfUpdateForm):
    class Meta(UserSelfUpdateForm.Meta):
        model = Admin


class SpecialistSelfUpdateForm(UserSelfUpdateForm):
    class Meta(UserSelfUpdateForm.Meta):
        model = Specialist


class ParentSelfUpdateForm(UserSelfUpdateForm):
    class Meta(UserSelfUpdateForm.Meta):
        model = Parent


class AdminMultiModelSelfUpdateForm(UserMultiModelUpdateForm):
    profile_related_name = "admin_profile"
    form_classes = {
        "user": AdminSelfUpdateForm,
        "profile": AdminProfileUpdateForm,
    }


class SpecialistMultiModelSelfUpdateForm(UserMultiModelUpdateForm):
    profile_related_name = "specialist_profile"
    form_classes = {
        "user": SpecialistSelfUpdateForm,
        "profile": SpecialistProfileUpdateForm,
    }


class ParentMultiModelSelfUpdateForm(UserMultiModelUpdateForm):
    profile_related_name = "parent_profile"
    form_classes = {
        "user": ParentSelfUpdateForm,
        "profile": ParentProfileUpdateForm,
    }


class UserSettingsForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    new_password = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(render_value=False),
    )
    confirm_password = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(render_value=False),
    )
    email_alerts = forms.BooleanField(required=False)
    weekly_report = forms.BooleanField(required=False)
    lgpd_data_export = forms.BooleanField(required=False)

    def __init__(self, *args, user: User, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        preferences = user.resolved_preferences
        
        from apps.users.enums import UserRole
        if user.role != UserRole.ADMIN:
            self.fields.pop("first_name", None)
            self.fields.pop("last_name", None)
            self.fields.pop("email_alerts", None)
            self.fields.pop("weekly_report", None)
            self.fields.pop("lgpd_data_export", None)
        else:
            self.initial.setdefault("first_name", user.first_name)
            self.initial.setdefault("last_name", user.last_name)
            for key, value in DEFAULT_USER_PREFERENCES.items():
                self.initial.setdefault(key, preferences.get(key, value))
        
        self.initial.setdefault("email", user.email)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise ValidationError(_("Um usuário com este e-mail já existe."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password or confirm_password:
            if new_password != confirm_password:
                self.add_error(
                    "confirm_password",
                    _("A confirmação da senha não confere."),
                )
            elif new_password:
                password_validation.validate_password(new_password, self.user)

        return cleaned_data

    def save(self) -> User:
        if "first_name" in self.cleaned_data:
            self.user.first_name = self.cleaned_data["first_name"]
        if "last_name" in self.cleaned_data:
            self.user.last_name = self.cleaned_data["last_name"]
            
        self.user.email = self.cleaned_data["email"]
        
        if "email_alerts" in self.cleaned_data:
            self.user.preferences = {
                "email_alerts": self.cleaned_data["email_alerts"],
                "weekly_report": self.cleaned_data["weekly_report"],
                "lgpd_data_export": self.cleaned_data["lgpd_data_export"],
            }

        new_password = self.cleaned_data.get("new_password")
        if new_password:
            self.user.set_password(new_password)
            self.user.password_changed_at = timezone.now()

        self.user.save()
        return self.user
