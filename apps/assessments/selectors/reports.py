from __future__ import annotations

from collections.abc import Mapping
from datetime import timedelta

from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.assessments import constants
from apps.assessments.selectors.evaluations import get_evaluations_queryset


def get_report_context(
    *, user, capabilities: Mapping[str, bool], filters: Mapping[str, object]
) -> dict[str, object]:
    queryset = get_evaluations_queryset(
        user=user,
        capabilities=capabilities,
    ).filter(
        status__in=(
            constants.EVALUATION_STATUS_COMPLETED,
            constants.EVALUATION_STATUS_REVIEWED,
        )
    )

    municipality = filters.get("municipality")
    if municipality:
        queryset = queryset.filter(municipality=municipality)

    period = int(filters.get("period") or 6)
    start_date = timezone.now() - timedelta(days=period * 30)
    queryset = queryset.filter(created__gte=start_date)

    total = queryset.count()
    risk_totals = {
        row["risk_level"]: row["total"]
        for row in queryset.values("risk_level").annotate(total=Count("id"))
    }
    risk_distribution = []
    for level, label in constants.RISK_LEVEL_CHOICES:
        value = risk_totals.get(level, 0)
        risk_distribution.append(
            {
                "level": level,
                "label": label,
                "value": value,
                "percent": int((value / total) * 100) if total else 0,
            }
        )

    subscale_alert_counter = dict.fromkeys(constants.EDSC_SUBSCALE_DEFINITIONS, 0)
    for row in queryset.values_list("subscale_scores", flat=True):
        if not isinstance(row, dict):
            continue
        for key, payload in row.items():
            if key in subscale_alert_counter and payload.get("is_alert"):
                subscale_alert_counter[key] += 1

    subscale_alerts = [
        {
            "key": key,
            "label": definition["label"],
            "value": subscale_alert_counter.get(key, 0),
        }
        for key, definition in constants.EDSC_SUBSCALE_DEFINITIONS.items()
    ]

    municipality_summary = (
        queryset.values("municipality__name")
        .annotate(
            total=Count("id"),
            high_risk=Count(
                "id",
                filter=Q(risk_level=constants.RISK_LEVEL_HIGH),
            ),
        )
        .order_by(
            "-total",
            "municipality__name",
        )
    )

    monthly_trend = (
        queryset.annotate(month=TruncMonth("created"))
        .values("month")
        .annotate(
            total=Count("id"),
            high_risk=Count(
                "id",
                filter=Q(risk_level=constants.RISK_LEVEL_HIGH),
            ),
        )
        .order_by("month")
    )

    return {
        "risk_distribution": risk_distribution,
        "subscale_alerts": subscale_alerts,
        "municipality_summary": municipality_summary,
        "monthly_trend": monthly_trend,
        "total_reports": total,
    }
