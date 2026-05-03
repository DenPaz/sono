from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("Basic information"),
            {
                "fields": (
                    "id",
                    "first_name",
                    "last_name",
                    "birth_date",
                    "biological_sex",
                    "notes",
                ),
            },
        ),
        (
            _("Relations"),
            {
                "fields": (
                    "parent",
                    "specialist",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_active",
                    "created",
                    "modified",
                ),
            },
        ),
    )
    list_display = [
        "id",
        "get_full_name",
        "age",
        "biological_sex",
        "parent_full_name",
        "specialist_full_name",
        "is_active",
    ]
    list_filter = [
        "biological_sex",
        "is_active",
    ]
    search_fields = [
        "parent__first_name",
        "parent__last_name",
        "specialist__first_name",
        "specialist__last_name",
    ]
    readonly_fields = [
        "id",
        "created",
        "modified",
    ]
    autocomplete_fields = [
        "parent",
        "specialist",
    ]
    list_per_page = 20
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).with_relations()

    @admin.display(description=_("Full name"))
    def get_full_name(self, obj):
        return obj.get_full_name()

    @admin.display(description=_("Parent"))
    def parent_full_name(self, obj):
        return obj.parent.get_full_name()

    @admin.display(description=_("Specialist"))
    def specialist_full_name(self, obj):
        return obj.specialist.get_full_name() if obj.specialist else None
