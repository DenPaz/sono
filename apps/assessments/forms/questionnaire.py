from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.assessments import constants
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import Municipality
from apps.assessments.models import normalize_child_name

INVALID_CHILD_NAME_PLACEHOLDERS = {
    "crianca sem identificacao",
    "criança sem identificação",
    "child without identification",
    "nao informado",
    "não informado",
    "sem identificacao",
    "sem identificação",
}

if TYPE_CHECKING:
    from collections.abc import Mapping


class QuestionnaireIdentificationForm(forms.ModelForm):
    municipality = forms.ModelChoiceField(
        label=_("Município"),
        queryset=Municipality.objects.none(),
        empty_label=_("Selecione"),
    )

    class Meta:
        model = AssessmentEvaluation
        fields = ["child_name", "child_age", "municipality"]
        labels = {
            "child_name": _("Nome da criança"),
            "child_age": _("Idade"),
        }
        widgets = {
            "child_name": forms.TextInput(
                attrs={
                    "class": "input w-full",
                    "placeholder": _("Ex.: Maria Silva"),
                }
            ),
            "child_age": forms.NumberInput(
                attrs={
                    "class": "input w-full",
                    "min": 0,
                    "max": 18,
                }
            ),
            "municipality": forms.Select(attrs={"class": "select w-full"}),
        }

    def __init__(
        self,
        *args,
        user=None,
        capabilities: dict[str, bool] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        can_view_all_assessments = bool(
            capabilities
            and capabilities.get(constants.CAPABILITY_VIEW_ALL_ASSESSMENTS, False)
        )
        if user and user.is_superuser:
            can_view_all_assessments = True

        if can_view_all_assessments:
            municipality_queryset = Municipality.objects.active()
        else:
            profile = getattr(user, "assessments_profile", None)
            municipality_id = getattr(profile, "municipality_id", None)
            municipality_queryset = Municipality.objects.active()
            if municipality_id:
                municipality_queryset = municipality_queryset.filter(id=municipality_id)
            else:
                municipality_queryset = municipality_queryset.none()

        self.fields["municipality"].queryset = municipality_queryset
        self.fields["child_name"].required = True

        if not self.is_bound and municipality_queryset.count() == 1:
            self.initial.setdefault("municipality", municipality_queryset.first())

        if not self.is_bound and self.instance and self.instance.pk:
            current_child_name = self.instance.get_child_name()
            if current_child_name:
                self.initial.setdefault("child_name", current_child_name)

    def clean_child_name(self) -> str:
        child_name = normalize_child_name(self.cleaned_data.get("child_name", ""))
        if not child_name:
            msg = _("Informe o nome da criança para continuar.")
            raise forms.ValidationError(msg)

        if child_name.casefold() in INVALID_CHILD_NAME_PLACEHOLDERS:
            msg = _("Informe o nome real da criança.")
            raise forms.ValidationError(msg)

        return child_name


class QuestionnaireStepForm(forms.Form):
    item_indexes: tuple[int, ...] = ()

    def __init__(self, *args, answers: Mapping[int, int] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        normalized_answers = dict(answers or {})

        for item_index in self.item_indexes:
            field_name = self.get_field_name(item_index=item_index)
            self.fields[field_name] = forms.TypedChoiceField(
                label=constants.EDSC_QUESTIONS[item_index],
                choices=constants.get_item_scale_choices(item_index=item_index),
                coerce=int,
                widget=forms.RadioSelect(
                    attrs={
                        "class": "radio radio-sm radio-primary",
                    }
                ),
            )
            if item_index in normalized_answers:
                self.initial[field_name] = normalized_answers[item_index]

    @staticmethod
    def get_field_name(*, item_index: int) -> str:
        return f"q_{item_index}"

    def cleaned_answers(self) -> dict[int, int]:
        return {
            item_index: int(
                self.cleaned_data[self.get_field_name(item_index=item_index)]
            )
            for item_index in self.item_indexes
        }


class QuestionnaireBlock1Form(QuestionnaireStepForm):
    item_indexes = constants.WIZARD_STEP_ITEM_INDEXES[1]


class QuestionnaireBlock2Form(QuestionnaireStepForm):
    item_indexes = constants.WIZARD_STEP_ITEM_INDEXES[2]


class QuestionnaireBlock3Form(QuestionnaireStepForm):
    item_indexes = constants.WIZARD_STEP_ITEM_INDEXES[3]


class QuestionnaireBlock4ReviewForm(QuestionnaireStepForm):
    item_indexes = constants.WIZARD_STEP_ITEM_INDEXES[4]
