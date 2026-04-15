from __future__ import annotations

from django.db.models import Count

from apps.assessments import constants
from apps.assessments.models import ProfessionalInvite
from apps.assessments.models import ProfessionalProfile


def get_professionals_table_data(*, user, capabilities):
    queryset = (
        ProfessionalProfile.objects.active()
        .select_related(
            "user",
            "municipality",
        )
        .annotate(total_evaluations=Count("user__assessments"))
    )

    can_manage_professionals = user.is_superuser or capabilities.get(
        constants.CAPABILITY_MANAGE_PROFESSIONALS,
        False,
    )
    if can_manage_professionals:
        return queryset

    return queryset.filter(user=user)


def get_recent_invites(*, user, capabilities, limit: int = 12):
    queryset = ProfessionalInvite.objects.select_related(
        "invited_by",
        "municipality",
    ).order_by("-created")

    can_manage_access = user.is_superuser or capabilities.get(
        constants.CAPABILITY_MANAGE_ACCESS,
        False,
    )
    if can_manage_access:
        return queryset[:limit]

    return queryset.filter(invited_by=user)[:limit]
