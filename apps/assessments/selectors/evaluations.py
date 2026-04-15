from __future__ import annotations

import re
from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.db.models import Q

from apps.assessments import constants
from apps.assessments.models import AssessmentEvaluation
from apps.assessments.models import compute_child_name_blind_index
from apps.assessments.models import normalize_child_name

if TYPE_CHECKING:
    from collections.abc import Mapping


def get_evaluations_queryset(*, user, capabilities: Mapping[str, bool]):
    can_view_all = capabilities.get(constants.CAPABILITY_VIEW_ALL_ASSESSMENTS, False)
    queryset = (
        AssessmentEvaluation.objects.select_related(
            "professional",
            "municipality",
        )
        .active()
        .visible_for_user(
            user=user,
            can_view_all_assessments=can_view_all,
        )
    )

    if user.is_superuser or can_view_all:
        return queryset

    user_profile = getattr(user, "assessments_profile", None)
    municipality_id = getattr(user_profile, "municipality_id", None)
    if not municipality_id:
        return queryset.none()

    return queryset.filter(municipality_id=municipality_id)


def apply_evaluations_filters(*, queryset, filters: Mapping[str, object]):
    search = filters.get("search")
    if search:
        normalized_search = normalize_child_name(str(search))
        search_query = Q(professional__first_name__icontains=search) | Q(
            professional__last_name__icontains=search
        )

        if normalized_search:
            blind_index = compute_child_name_blind_index(normalized_search)
            search_query |= Q(child_name_blind_index=blind_index)

            normalized_reference = normalized_search.casefold().replace(" ", "")
            if normalized_reference.startswith("cr-"):
                normalized_reference = normalized_reference[3:]

            if re.fullmatch(r"[0-9a-f]{4,64}", normalized_reference):
                search_query |= Q(
                    child_name_blind_index__istartswith=normalized_reference
                )

        queryset = queryset.filter(search_query)

    status = filters.get("status")
    if status:
        queryset = queryset.filter(status=status)

    risk_level = filters.get("risk_level")
    if risk_level:
        queryset = queryset.filter(risk_level=risk_level)

    municipality = filters.get("municipality")
    if municipality:
        queryset = queryset.filter(municipality=municipality)

    professional = filters.get("professional")
    if professional:
        queryset = queryset.filter(professional=professional)

    return queryset.order_by("-modified")


def get_evaluations_page(
    *,
    user,
    capabilities: Mapping[str, bool],
    filters: Mapping[str, object],
    page_number: str | int = 1,
    per_page: int = 10,
):
    queryset = get_evaluations_queryset(
        user=user,
        capabilities=capabilities,
    )
    filtered_queryset = apply_evaluations_filters(
        queryset=queryset,
        filters=filters,
    )
    paginator = Paginator(filtered_queryset, per_page)
    return paginator.get_page(page_number)


def get_recent_evaluations(*, user, capabilities: Mapping[str, bool], limit: int = 8):
    queryset = get_evaluations_queryset(
        user=user,
        capabilities=capabilities,
    )
    return queryset.order_by("-modified")[:limit]
