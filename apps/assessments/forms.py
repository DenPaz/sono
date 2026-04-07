from django import forms
from django.utils.translation import gettext_lazy as _

BLOCK_TWO_QUESTIONS = [
    ("q01", _("Senti dificuldade para iniciar o sono.")),
    ("q02", _("Acordei durante a noite com frequencia.")),
    ("q03", _("Acordei mais cedo do que o planejado.")),
    ("q04", _("Senti sonolencia excessiva ao longo do dia.")),
    ("q05", _("Percebi irritabilidade acima do habitual.")),
    ("q06", _("Senti ansiedade antes de dormir.")),
    ("q07", _("Tive preocupacoes persistentes durante a noite.")),
    ("q08", _("Acordei com sensacao de cansaco.")),
    ("q09", _("Observei dificuldade de concentracao.")),
    ("q10", _("Tive lapsos de memoria no dia a dia.")),
    ("q11", _("Percebi queda de produtividade no trabalho.")),
    ("q12", _("Senti dificuldade para tomar decisoes.")),
    ("q13", _("Evitei atividades sociais por cansaco.")),
    ("q14", _("Tive conflitos familiares relacionados ao sono.")),
    ("q15", _("Percebi piora do humor em interacoes sociais.")),
    ("q16", _("Senti isolamento por indisposicao.")),
    ("q17", _("Senti reducao importante de energia fisica.")),
    ("q18", _("Precisei de repouso durante o horario de trabalho.")),
    ("q19", _("Tive queda de desempenho em tarefas simples.")),
    ("q20", _("Senti exaustao ao final da manha.")),
    ("q21", _("Usei estimulantes para me manter acordado.")),
    ("q22", _("Aumentei consumo de cafeina para render.")),
    ("q23", _("Percebi piora de habitos alimentares por cansaco.")),
    ("q24", _("Tive dificuldade para manter rotina regular de sono.")),
]

SUBSCALE_GROUPS = {
    "sono": ("q01", "q02", "q03", "q04"),
    "emocional": ("q05", "q06", "q07", "q08"),
    "cognitivo": ("q09", "q10", "q11", "q12"),
    "social": ("q13", "q14", "q15", "q16"),
    "energia": ("q17", "q18", "q19", "q20"),
    "comportamental": ("q21", "q22", "q23", "q24"),
}

SUBSCALE_LABELS = {
    "sono": _("Qualidade do Sono"),
    "emocional": _("Impacto Emocional"),
    "cognitivo": _("Impacto Cognitivo"),
    "social": _("Impacto Social"),
    "energia": _("Energia Diurna"),
    "comportamental": _("Comportamentos Associados"),
}


class PatientDataForm(forms.Form):
    patient_name = forms.CharField(
        label=_("Nome do paciente"),
        max_length=150,
    )
    patient_birth_date = forms.DateField(
        label=_("Data de nascimento"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    municipality = forms.CharField(
        label=_("Municipio"),
        max_length=120,
    )
    professional_name = forms.CharField(
        label=_("Profissional responsavel"),
        max_length=150,
    )


class BlockOneForm(forms.Form):
    SCREENING_CHOICES = [
        ("sim", _("Sim")),
        ("nao", _("Nao")),
    ]

    screening_q1 = forms.ChoiceField(
        label=_(
            "Nas ultimas duas semanas houve piora perceptivel da qualidade do sono?",
        ),
        choices=SCREENING_CHOICES,
        widget=forms.Select,
    )
    screening_q2 = forms.ChoiceField(
        label=_("Existe impacto clinico relevante no funcionamento diario?"),
        choices=SCREENING_CHOICES,
        widget=forms.Select,
    )


class BlockTwoForm(forms.Form):
    SCALE_CHOICES = [
        (0, _("Nunca")),
        (1, _("Raramente")),
        (2, _("Frequentemente")),
        (3, _("Quase sempre")),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question_key, question_label in BLOCK_TWO_QUESTIONS:
            self.fields[question_key] = forms.TypedChoiceField(
                label=question_label,
                choices=self.SCALE_CHOICES,
                coerce=int,
                widget=forms.Select,
            )
