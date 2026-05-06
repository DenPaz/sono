from betterforms.multiform import MultiModelForm
from django import forms
from django.contrib.auth.hashers import make_password

from .models import Admin
from .models import AdminProfile
from .models import Parent
from .models import ParentProfile
from .models import Specialist
from .models import SpecialistProfile


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
    class Meta(UserCreateForm.Meta):
        model = Parent


class ParentUpdateForm(UserUpdateForm):
    class Meta(UserUpdateForm.Meta):
        model = Parent


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
