from __future__ import annotations

from collections.abc import Mapping

from django.db.models import Count

from apps.assessments import constants
from apps.assessments.selectors.evaluations import get_evaluations_queryset
from apps.assessments.selectors.evaluations import get_recent_evaluations


def get_overview_context(
    *, user, capabilities: Mapping[str, bool]
) -> dict[str, object]:
    queryset = get_evaluations_queryset(
        user=user,
        capabilities=capabilities,
    )

    total = queryset.count()
    draft_total = queryset.filter(status=constants.EVALUATION_STATUS_DRAFT).count()
    concluded_total = queryset.filter(
        status__in=(
            constants.EVALUATION_STATUS_COMPLETED,
            constants.EVALUATION_STATUS_REVIEWED,
        )
    ).count()
    high_risk_total = queryset.filter(risk_level=constants.RISK_LEVEL_HIGH).count()

    grouped_risk = {
        row["risk_level"]: row["total"]
        for row in queryset.values("risk_level").annotate(total=Count("id"))
    }
    risk_indicators = [
        {
            "level": level,
            "label": label,
            "total": grouped_risk.get(level, 0),
        }
        for level, label in constants.RISK_LEVEL_CHOICES
    ]

    return {
        "kpis": {
            "total": total,
            "draft_total": draft_total,
            "concluded_total": concluded_total,
            "high_risk_total": high_risk_total,
        },
        "risk_indicators": risk_indicators,
        "recent_queue": get_recent_evaluations(
            user=user,
            capabilities=capabilities,
            limit=8,
        ),
    }
