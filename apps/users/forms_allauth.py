from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _


class UserSignupForm(SignupForm):
    first_name = forms.CharField(
        label=_("Nome"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Nome")}),
    )
    last_name = forms.CharField(
        label=_("Sobrenome"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Sobrenome")}),
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user
