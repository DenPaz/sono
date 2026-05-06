from django import forms
from django.utils.translation import gettext_lazy as _

from apps.patients.forms import QuestionnaireStep1Form
from apps.patients.forms import QuestionnaireStep2Form
from apps.patients.forms import QuestionnaireStep3Form
from apps.patients.forms import QuestionnaireStep4Form
from apps.patients.forms import QuestionnaireStep5Form
from apps.patients.forms import STEP_TITLES
from apps.patients.models import Patient


from apps.patients.enums import BiologicalSex

class AssessmentPatientForm(forms.Form):
    first_name = forms.CharField(
        label=_("Nome"),
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": _("Primeiro nome"),
            }
        ),
    )
    last_name = forms.CharField(
        label=_("Sobrenome"),
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": _("Sobrenome completo"),
            }
        ),
    )
    parent = forms.ModelChoiceField(
        queryset=None,
        label=_("Responsável (Opcional)"),
        required=False,
        help_text=_("Vincule este paciente a um responsável cadastrado."),
        widget=forms.Select(
            attrs={"class": "select select-bordered w-full"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.users.models import Parent
        self.fields["parent"].queryset = Parent.objects.all()
        self.fields["parent"].empty_label = _("Nenhum responsável selecionado")
    birth_date = forms.DateField(
        label=_("Data de Nascimento"),
        widget=forms.DateInput(
            attrs={
                "class": "input input-bordered w-full",
                "type": "date",
            }
        ),
    )
    biological_sex = forms.ChoiceField(
        label=_("Sexo Biológico"),
        choices=BiologicalSex.choices,
        widget=forms.Select(
            attrs={"class": "select select-bordered w-full"}
        ),
    )
    municipality = forms.CharField(
        label=_("Município"),
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": _("Cidade / Município"),
            }
        ),
    )
    notes = forms.CharField(
        label=_("Observações"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 3,
                "placeholder": _("Observações adicionais sobre o paciente"),
            }
        ),
    )


QUESTIONNAIRE_FORMS = [
    ("patient", AssessmentPatientForm),
    ("step1", QuestionnaireStep1Form),
    ("step2", QuestionnaireStep2Form),
    ("step3", QuestionnaireStep3Form),
    ("step4", QuestionnaireStep4Form),
    ("step5", QuestionnaireStep5Form),
]

STEP_METADATA = {
    "patient": {
        "title": _("Paciente"),
        "description": _("Informe o nome do paciente para iniciar o questionário."),
    },
    "step1": {
        "title": STEP_TITLES.get("step1", _("Etapa 1")),
        "description": _("Duração e início do sono."),
    },
    "step2": {
        "title": STEP_TITLES.get("step2", _("Etapa 2")),
        "description": _("Comportamento ao dormir."),
    },
    "step3": {
        "title": STEP_TITLES.get("step3", _("Etapa 3")),
        "description": _("Despertares noturnos e respiração."),
    },
    "step4": {
        "title": STEP_TITLES.get("step4", _("Etapa 4")),
        "description": _("Parassonias e despertares."),
    },
    "step5": {
        "title": STEP_TITLES.get("step5", _("Etapa 5")),
        "description": _("Sonolência diurna."),
    },
}
