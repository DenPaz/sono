from __future__ import annotations

from datetime import timedelta

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.assessments import constants
from apps.assessments.selectors.evaluations import get_evaluations_queryset


def get_municipality_ranking(
    *,
    user,
    capabilities,
    period_months: int = 6,
    municipality_id: str | None = None,
):
    queryset = get_evaluations_queryset(
        user=user,
        capabilities=capabilities,
    ).completed()

    start_date = timezone.now() - timedelta(days=period_months * 30)
    queryset = queryset.filter(created__gte=start_date)

    if municipality_id:
        queryset = queryset.filter(municipality_id=municipality_id)

    return (
        queryset.values(
            "municipality__id",
            "municipality__name",
            "municipality__state_code",
        )
        .annotate(
            total_evaluations=Count("id"),
            high_risk_total=Count(
                "id",
                filter=Q(risk_level=constants.RISK_LEVEL_HIGH),
            ),
            average_score=Avg("total_score"),
        )
        .order_by(
            "-high_risk_total",
            "-total_evaluations",
            "municipality__name",
        )
    )


def get_municipality_trend(
    *,
    user,
    capabilities,
    period_months: int = 6,
    municipality_id: str | None = None,
):
    queryset = get_evaluations_queryset(
        user=user,
        capabilities=capabilities,
    ).completed()

    start_date = timezone.now() - timedelta(days=period_months * 30)
    queryset = queryset.filter(created__gte=start_date)
    if municipality_id:
        queryset = queryset.filter(municipality_id=municipality_id)

    return (
        queryset.annotate(month=TruncMonth("created"))
        .values(
            "month",
            "municipality__name",
        )
        .annotate(
            total_evaluations=Count("id"),
            high_risk_total=Count(
                "id",
                filter=Q(risk_level=constants.RISK_LEVEL_HIGH),
            ),
            average_score=Avg("total_score"),
        )
        .order_by(
            "-month",
            "municipality__name",
        )
    )
