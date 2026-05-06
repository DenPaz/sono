from django import forms
from django.utils.translation import gettext_lazy as _

from .enums import QuestionnaireFrequency
from .enums import SleepDuration
from .enums import SleepOnsetDelay
from .models import Patient


class PatientCreateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "biological_sex",
            "notes",
            "parent",
            "specialist",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "biological_sex",
            "notes",
            "parent",
            "specialist",
            "is_active",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


def frequency_field(label: str, **kwargs) -> forms.ChoiceField:
    return forms.TypedChoiceField(
        label=label,
        choices=QuestionnaireFrequency.choices,
        coerce=int,
        widget=forms.RadioSelect,
        **kwargs,
    )


class QuestionnaireStep1Form(forms.Form):
    q1 = forms.TypedChoiceField(
        label=_("How many hours does the child sleep per night?"),
        choices=SleepDuration.choices,
        coerce=int,
        widget=forms.RadioSelect,
    )
    q2 = forms.TypedChoiceField(
        label=_("How long does the child take to fall asleep?"),
        choices=SleepOnsetDelay.choices,
        coerce=int,
        widget=forms.RadioSelect,
    )


class QuestionnaireStep2Form(forms.Form):
    q3 = frequency_field(
        label=_("The child refuses to go to bed to sleep."),
    )
    q4 = frequency_field(
        label=_("The child has difficulty falling asleep."),
    )
    q5 = frequency_field(
        label=_("The child feels anxious or afraid when falling asleep."),
    )
    q6 = frequency_field(
        label=_("The child has sudden jerks or body tremors at sleep onset."),
    )
    q7 = frequency_field(
        label=_("The child makes rhythmic movements with their head or body at night."),
    )
    q8 = frequency_field(
        label=_("The child says they see 'strange things' just before falling asleep."),
    )
    q9 = frequency_field(
        label=_("The child sweats a lot when falling asleep."),
    )


class QuestionnaireStep3Form(forms.Form):
    q10 = frequency_field(
        label=_("The child wakes up more than twice during the night."),
    )
    q11 = frequency_field(
        label=_("The child wakes up at night and has difficulty falling back asleep."),
    )
    q12 = frequency_field(
        label=_("The child moves continuously during sleep."),
    )
    q13 = frequency_field(
        label=_("The child does not breathe well during sleep."),
    )
    q14 = frequency_field(
        label=_("The child pauses breathing for a few moments during sleep."),
    )
    q15 = frequency_field(
        label=_("The child snores."),
    )
    q16 = frequency_field(
        label=_("The child sweats a lot during the night."),
    )


class QuestionnaireStep4Form(forms.Form):
    q17 = frequency_field(
        label=_("The child gets up and sits or walks around in bed while asleep."),
    )
    q18 = frequency_field(
        label=_("The child talks during sleep."),
    )
    q19 = frequency_field(
        label=_("The child grinds their teeth during sleep."),
    )
    q20 = frequency_field(
        label=_(
            "The child screams in distress during sleep without being able to wake up."
        ),
    )
    q21 = frequency_field(
        label=_("The child has nightmares they don't remember the next day."),
    )


class QuestionnaireStep5Form(forms.Form):
    q22 = frequency_field(
        label=_("The child has difficulty waking up in the morning."),
    )
    q23 = frequency_field(
        label=_("The child wakes up tired in the morning."),
    )
    q24 = frequency_field(
        label=_(
            "Upon waking, the child cannot move or feels paralysed for a few minutes."
        ),
    )
    q25 = frequency_field(
        label=_("The child feels sleepy during the day."),
    )
    q26 = frequency_field(
        label=_("The child falls asleep in unexpected situations during the day."),
    )


QUESTIONNAIRE_FORMS = [
    ("step1", QuestionnaireStep1Form),
    ("step2", QuestionnaireStep2Form),
    ("step3", QuestionnaireStep3Form),
    ("step4", QuestionnaireStep4Form),
    ("step5", QuestionnaireStep5Form),
]

STEP_TITLES = {
    "step1": _("Sleep duration & onset"),
    "step2": _("Bedtime behaviour"),
    "step3": _("Night awakenings & breathing"),
    "step4": _("Arousal & parasomnias"),
    "step5": _("Daytime sleepiness"),
}
