from django.utils.translation import gettext_lazy as _

ROLE_PROFESSIONAL = "PROFISSIONAL"
ROLE_CHIEF_ADMIN = "CHEFE_ADMIN"
ASSESSMENT_ROLES = (ROLE_PROFESSIONAL, ROLE_CHIEF_ADMIN)

CAPABILITY_VIEW_ALL_ASSESSMENTS = "can_view_all_assessments"
CAPABILITY_MANAGE_PROFESSIONALS = "can_manage_professionals"
CAPABILITY_INVITE_PROFESSIONAL = "can_invite_professional"
CAPABILITY_EXPORT_REPORTS = "can_export_reports"
CAPABILITY_MANAGE_ACCESS = "can_manage_access"

ASSESSMENT_CAPABILITIES = (
    CAPABILITY_VIEW_ALL_ASSESSMENTS,
    CAPABILITY_MANAGE_PROFESSIONALS,
    CAPABILITY_INVITE_PROFESSIONAL,
    CAPABILITY_EXPORT_REPORTS,
    CAPABILITY_MANAGE_ACCESS,
)

EVALUATION_STATUS_DRAFT = "rascunho"
EVALUATION_STATUS_COMPLETED = "concluida"
EVALUATION_STATUS_REVIEWED = "revisada"

EVALUATION_STATUS_CHOICES = (
    (EVALUATION_STATUS_DRAFT, _("Rascunho")),
    (EVALUATION_STATUS_COMPLETED, _("Concluída")),
    (EVALUATION_STATUS_REVIEWED, _("Revisada")),
)

RISK_LEVEL_NO_ALERT = "sem_alerta"
RISK_LEVEL_ATTENTION = "atencao"
RISK_LEVEL_HIGH = "alto_risco"

RISK_LEVEL_CHOICES = (
    (RISK_LEVEL_NO_ALERT, _("Sem alerta")),
    (RISK_LEVEL_ATTENTION, _("Atenção")),
    (RISK_LEVEL_HIGH, _("Alto risco")),
)

EDSC_MIN_ITEM_VALUE = 1
EDSC_MAX_ITEM_VALUE = 5
EDSC_ITEMS_COUNT = 26
EDSC_MIN_TOTAL_SCORE = EDSC_ITEMS_COUNT * EDSC_MIN_ITEM_VALUE
EDSC_MAX_TOTAL_SCORE = EDSC_ITEMS_COUNT * EDSC_MAX_ITEM_VALUE

EDSC_STANDARD_SCALE_CHOICES = (
    (1, _("Nunca")),
    (2, _("Ocasionalmente (1 ou 2 vezes por mês)")),
    (3, _("Algumas vezes (1 ou 2 vezes por semana)")),
    (4, _("Quase sempre (3 a 5 vezes por semana)")),
    (5, _("Sempre (todos os dias)")),
)

EDSC_ITEM_1_SCALE_CHOICES = (
    (1, _("9-11 horas")),
    (2, _("8-9 horas")),
    (3, _("7-8 horas")),
    (4, _("5-7 horas")),
    (5, _("Menos de 5 horas")),
)

EDSC_ITEM_2_SCALE_CHOICES = (
    (1, _("Menos de 15 min")),
    (2, _("15-30 min")),
    (3, _("30-45 min")),
    (4, _("45-60 min")),
    (5, _("Mais de 60 min")),
)

EDSC_ITEM_1_INDEX = 1
EDSC_ITEM_2_INDEX = 2

EDSC_QUESTIONS = {
    1: _("Quantas horas a criança dorme durante a noite?"),
    2: _("Quanto tempo a criança demora para adormecer?"),
    3: _("A criança não quer ir para a cama para dormir"),
    4: _("A criança tem dificuldade para adormecer"),
    5: _("Antes de adormecer a criança está agitada, nervosa ou sente medo"),
    6: _(
        'A criança apresenta "movimentos bruscos", repuxões ou tremores ao adormecer'
    ),
    7: _("Durante a noite a criança faz movimentos rítmicos com a cabeça e corpo"),
    8: _(
        'A criança diz que está vendo "coisas estranhas" um pouco antes de adormecer'
    ),
    9: _("A criança transpira muito ao adormecer"),
    10: _("A criança acorda mais de duas vezes durante a noite"),
    11: _("A criança acorda durante a noite e tem dificuldade em adormecer novamente"),
    12: _("A criança mexe-se continuamente durante o sono"),
    13: _("A criança não respira bem durante o sono"),
    14: _("A criança para de respirar por alguns instantes durante o sono"),
    15: _("A criança ronca"),
    16: _("A criança transpira muito durante a noite"),
    17: _("A criança levanta-se e senta-se na cama ou anda enquanto dorme"),
    18: _("A criança fala durante o sono"),
    19: _("A criança range os dentes durante o sono"),
    20: _("Durante o sono a criança grita angustiada, sem conseguir acordar"),
    21: _("A criança tem pesadelos que não lembra no dia seguinte"),
    22: _("A criança tem dificuldade em acordar pela manhã"),
    23: _("Acorda cansada pela manhã"),
    24: _(
        "Ao acordar a criança não consegue movimentar-se ou fica "
        "como se estivesse paralisada por uns minutos"
    ),
    25: _("A criança sente-se sonolenta durante o dia"),
    26: _("Durante o dia a criança adormece em situações inesperadas sem avisar"),
}

EDSC_SUBSCALE_DEFINITIONS = {
    "disturbios_inicio_manutencao_sono": {
        "label": _("Distúrbios de Início e Manutenção do Sono"),
        "item_indexes": (1, 2, 3, 4, 5, 10, 11),
        "acceptable_max": 21,
    },
    "disturbios_respiratorios_sono": {
        "label": _("Distúrbios Respiratórios do Sono"),
        "item_indexes": (13, 14, 15),
        "acceptable_max": 6,
    },
    "disturbios_despertar": {
        "label": _("Distúrbios do Despertar"),
        "item_indexes": (17, 20, 21),
        "acceptable_max": 11,
    },
    "disturbios_transicao_sono_vigilia": {
        "label": _("Distúrbios da Transição Sono-Vigília"),
        "item_indexes": (6, 7, 8, 12, 18, 19),
        "acceptable_max": 23,
    },
    "sonolencia_excessiva_diurna": {
        "label": _("Sonolência Excessiva Diurna"),
        "item_indexes": (22, 23, 24, 25, 26),
        "acceptable_max": 19,
    },
    "hiperhidrose_sono": {
        "label": _("Hiperhidrose do Sono"),
        "item_indexes": (9, 16),
        "acceptable_max": 7,
    },
}

WIZARD_TOTAL_STEPS = 5
WIZARD_IDENTIFICATION_STEP = 0
WIZARD_STEP_ITEM_INDEXES = {
    1: (1, 2, 3, 4, 5, 6, 7),
    2: (8, 9, 10, 11, 12, 13, 14),
    3: (15, 16, 17, 18, 19, 20, 21),
    4: (22, 23, 24, 25, 26),
}


def get_item_scale_choices(item_index: int) -> tuple[tuple[int, str], ...]:
    if item_index == EDSC_ITEM_1_INDEX:
        return EDSC_ITEM_1_SCALE_CHOICES
    if item_index == EDSC_ITEM_2_INDEX:
        return EDSC_ITEM_2_SCALE_CHOICES
    return EDSC_STANDARD_SCALE_CHOICES
