from __future__ import annotations

from apps.assessments import constants


def get_assessment_capabilities(*, user) -> dict[str, bool]:
    default_caps = dict.fromkeys(constants.ASSESSMENT_CAPABILITIES, False)

    if not user.is_authenticated:
        return default_caps

    if user.is_superuser:
        return dict.fromkeys(constants.ASSESSMENT_CAPABILITIES, True)

    group_names = set(user.groups.values_list("name", flat=True))
    if constants.ROLE_CHIEF_ADMIN in group_names:
        return dict.fromkeys(constants.ASSESSMENT_CAPABILITIES, True)

    if constants.ROLE_PROFESSIONAL in group_names:
        return {
            constants.CAPABILITY_VIEW_ALL_ASSESSMENTS: False,
            constants.CAPABILITY_MANAGE_PROFESSIONALS: False,
            constants.CAPABILITY_INVITE_PROFESSIONAL: False,
            constants.CAPABILITY_EXPORT_REPORTS: True,
            constants.CAPABILITY_MANAGE_ACCESS: False,
        }

    return {
        constants.CAPABILITY_VIEW_ALL_ASSESSMENTS: bool(user.is_staff),
        constants.CAPABILITY_MANAGE_PROFESSIONALS: False,
        constants.CAPABILITY_INVITE_PROFESSIONAL: False,
        constants.CAPABILITY_EXPORT_REPORTS: True,
        constants.CAPABILITY_MANAGE_ACCESS: False,
    }
