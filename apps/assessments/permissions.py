from __future__ import annotations

from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _

from apps.assessments import constants
from apps.assessments.services.capabilities import get_assessment_capabilities


def ensure_assessment_groups() -> None:
    for role_name in constants.ASSESSMENT_ROLES:
        Group.objects.get_or_create(name=role_name)


def user_has_role(*, user, role_name: str) -> bool:
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=role_name).exists()


def require_assessment_capability(
    *, request: HttpRequest, capability: str
) -> HttpResponseForbidden | None:
    caps = get_assessment_capabilities(user=request.user)
    if caps.get(capability, False):
        return None
    return HttpResponseForbidden(_("Você não possui permissão para esta ação."))
