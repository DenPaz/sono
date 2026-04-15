from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.assessments import constants
from apps.assessments.models import Municipality

User = get_user_model()


def _can_view_all_assessments(*, capabilities: dict[str, bool] | None) -> bool:
    if not capabilities:
        return False
    return bool(capabilities.get(constants.CAPABILITY_VIEW_ALL_ASSESSMENTS, False))


def _get_user_municipality_queryset(*, user):
    queryset = Municipality.objects.active()
    profile = getattr(user, "assessments_profile", None)
    municipality_id = getattr(profile, "municipality_id", None)
    if not municipality_id:
        return queryset.none()
    return queryset.filter(id=municipality_id)


class EvaluationsFilterForm(forms.Form):
    search = forms.CharField(
        label=_("Busca"),
        required=False,
    )
    status = forms.ChoiceField(
        label=_("Status"),
        required=False,
        choices=(("", _("Todos")), *constants.EVALUATION_STATUS_CHOICES),
    )
    risk_level = forms.ChoiceField(
        label=_("Risco"),
        required=False,
        choices=(("", _("Todos")), *constants.RISK_LEVEL_CHOICES),
    )
    municipality = forms.ModelChoiceField(
        label=_("Município"),
        required=False,
        queryset=Municipality.objects.none(),
    )
    professional = forms.ModelChoiceField(
        label=_("Profissional"),
        required=False,
        queryset=User.objects.none(),
    )

    def __init__(
        self,
        *args,
        show_professional_filter: bool = False,
        user=None,
        capabilities: dict[str, bool] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        can_view_all = show_professional_filter or _can_view_all_assessments(
            capabilities=capabilities
        )

        if can_view_all:
            self.fields["municipality"].queryset = Municipality.objects.active()
        else:
            self.fields["municipality"].queryset = _get_user_municipality_queryset(
                user=user
            )

        self.fields["professional"].queryset = User.objects.filter(
            is_active=True
        ).order_by(
            "first_name",
            "last_name",
        )
        if not can_view_all:
            self.fields.pop("professional")


class MunicipalityPeriodFilterBase(forms.Form):
    municipality = forms.ModelChoiceField(
        label=_("Município"),
        required=False,
        queryset=Municipality.objects.none(),
    )
    period = forms.ChoiceField(
        label=_("Período"),
        required=False,
        choices=(
            ("3", _("Últimos 3 meses")),
            ("6", _("Últimos 6 meses")),
            ("12", _("Últimos 12 meses")),
        ),
        initial="6",
    )

    def __init__(
        self,
        *args,
        user=None,
        capabilities: dict[str, bool] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if _can_view_all_assessments(capabilities=capabilities):
            self.fields["municipality"].queryset = Municipality.objects.active()
        else:
            self.fields["municipality"].queryset = _get_user_municipality_queryset(
                user=user
            )


class MunicipalityFiltersForm(MunicipalityPeriodFilterBase):
    pass


class ReportFiltersForm(MunicipalityPeriodFilterBase):
    pass
