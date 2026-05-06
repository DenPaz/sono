import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .enums import BiologicalSex
from .models import Patient


class PatientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        label=_("Search"),
        method="filter_search",
    )
    biological_sex = django_filters.ChoiceFilter(
        label=_("Biological sex"),
        choices=[("", _("All")), *BiologicalSex.choices],
        empty_label=None,
    )
    is_active = django_filters.ChoiceFilter(
        label=_("Status"),
        choices=[
            ("", _("All")),
            ("true", _("Active")),
            ("false", _("Inactive")),
        ],
        method="filter_is_active",
        empty_label=None,
    )

    class Meta:
        model = Patient
        fields = ["search", "biological_sex", "is_active"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(parent__first_name__icontains=value)
            | Q(parent__last_name__icontains=value)
            | Q(specialist__first_name__icontains=value)
            | Q(specialist__last_name__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        if value == "true":
            return queryset.filter(is_active=True)
        if value == "false":
            return queryset.filter(is_active=False)
        return queryset
