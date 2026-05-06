from django.utils.translation import gettext_lazy as _

SUBSCALE_CONFIG = [
    (
        "sleep_onset_maintenance",
        _("Início e manutenção do sono"),
        "sleep_onset_maintenance_score",
        35,
    ),
    ("respiratory", _("Respiratório"), "respiratory_score", 15),
    ("arousal", _("Despertares"), "arousal_score", 15),
    (
        "sleep_wake_transition",
        _("Transição sono-vigília"),
        "sleep_wake_transition_score",
        30,
    ),
    (
        "excessive_daytime_sleepiness",
        _("Sonolência diurna"),
        "excessive_daytime_sleepiness_score",
        25,
    ),
    ("hyperhidrosis", _("Hiperidrose"), "hyperhidrosis_score", 10),
]

TOTAL_MAX_SCORE = sum(item[3] for item in SUBSCALE_CONFIG)


def build_risk_summary(flags: dict[str, bool]) -> dict:
    flagged_count = sum(1 for value in flags.values() if value)
    if flagged_count >= 3:
        return {
            "label": _("Alto"),
            "badge": "badge-error",
            "description": _(
                "Múltiplos alertas clínicos. Priorize acompanhamento.",
            ),
        }
    if flagged_count >= 1:
        return {
            "label": _("Moderado"),
            "badge": "badge-warning",
            "description": _(
                "Alertas identificados. Recomendado acompanhamento.",
            ),
        }
    return {
        "label": _("Baixo"),
        "badge": "badge-success",
        "description": _("Sem alertas clínicos relevantes."),
    }


def build_subscale_breakdown(response) -> list[dict]:
    subscales = []
    for key, label, attr_name, max_score in SUBSCALE_CONFIG:
        score = getattr(response, attr_name, 0)
        percentage = round((score / max_score) * 100) if max_score else 0
        subscales.append(
            {
                "key": key,
                "label": label,
                "score": score,
                "max_score": max_score,
                "percentage": percentage,
                "flagged": response.flags.get(key, False),
            }
        )
    return subscales
