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
        label=_("1. Quantas horas a criança dorme durante a noite?"),
        choices=SleepDuration.choices,
        coerce=int,
        widget=forms.RadioSelect,
    )
    q2 = forms.TypedChoiceField(
        label=_("2. Quanto tempo a criança demora para adormecer?"),
        choices=SleepOnsetDelay.choices,
        coerce=int,
        widget=forms.RadioSelect,
    )


class QuestionnaireStep2Form(forms.Form):
    q3 = frequency_field(
        label=_("3. A criança não quer ir para a cama para dormir."),
    )
    q4 = frequency_field(
        label=_("4. A criança tem dificuldade para adormecer."),
    )
    q5 = frequency_field(
        label=_("5. Antes de adormecer a criança está agitada, nervosa ou sente medo."),
    )
    q6 = frequency_field(
        label=_("6. A criança apresenta \"movimentos bruscos\", repuxões ou tremores ao adormecer."),
    )
    q7 = frequency_field(
        label=_("7. Durante a noite a criança faz movimentos rítmicos com a cabeça e corpo."),
    )
    q8 = frequency_field(
        label=_("8. A criança diz que está vendo \"coisas estranhas\" um pouco antes de adormecer."),
    )
    q9 = frequency_field(
        label=_("9. A criança transpira muito ao adormecer."),
    )


class QuestionnaireStep3Form(forms.Form):
    q10 = frequency_field(
        label=_("10. A criança acorda mais de duas vezes durante a noite."),
    )
    q11 = frequency_field(
        label=_("11. A criança acorda durante a noite e tem dificuldade em adormecer novamente."),
    )
    q12 = frequency_field(
        label=_("12. A criança mexe-se continuamente durante o sono."),
    )
    q13 = frequency_field(
        label=_("13. A criança não respira bem durante o sono."),
    )
    q14 = frequency_field(
        label=_("14. A criança para de respirar por alguns instantes durante o sono."),
    )
    q15 = frequency_field(
        label=_("15. A criança ronca."),
    )
    q16 = frequency_field(
        label=_("16. A criança transpira muito durante a noite."),
    )


class QuestionnaireStep4Form(forms.Form):
    q17 = frequency_field(
        label=_("17. A criança levanta-se e senta-se na cama ou anda enquanto dorme."),
    )
    q18 = frequency_field(
        label=_("18. A criança fala durante o sono."),
    )
    q19 = frequency_field(
        label=_("19. A criança range os dentes durante o sono."),
    )
    q20 = frequency_field(
        label=_("20. Durante o sono a criança grita angustiada, sem conseguir acordar."),
    )
    q21 = frequency_field(
        label=_("21. A criança tem pesadelos que não lembra no dia seguinte."),
    )


class QuestionnaireStep5Form(forms.Form):
    q22 = frequency_field(
        label=_("22. A criança tem dificuldade em acordar pela manhã."),
    )
    q23 = frequency_field(
        label=_("23. Acorda cansada, pela manhã."),
    )
    q24 = frequency_field(
        label=_("24. Ao acordar a criança não consegue movimentar-se ou fica como se estivesse paralisada por uns minutos."),
    )
    q25 = frequency_field(
        label=_("25. A criança sente-se sonolenta durante o dia."),
    )
    q26 = frequency_field(
        label=_("26. Durante o dia a criança adormece em situações inesperadas sem avisar."),
    )


QUESTIONNAIRE_FORMS = [
    ("step1", QuestionnaireStep1Form),
    ("step2", QuestionnaireStep2Form),
    ("step3", QuestionnaireStep3Form),
    ("step4", QuestionnaireStep4Form),
    ("step5", QuestionnaireStep5Form),
]

STEP_TITLES = {
    "step1": _("Duração e início do sono"),
    "step2": _("Comportamento ao dormir"),
    "step3": _("Despertares noturnos e respiração"),
    "step4": _("Despertares e parassonias"),
    "step5": _("Sonolência diurna"),
}
