import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .enums import UserRole
from .models import User


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        label=_("Search"),
        method="filter_search",
    )
    role = django_filters.ChoiceFilter(
        label=_("Role"),
        choices=[("", _("All")), *UserRole.choices],
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
        model = User
        fields = ["search", "role", "is_active"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(email__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        if value == "true":
            return queryset.filter(is_active=True)
        if value == "false":
            return queryset.filter(is_active=False)
        return queryset
