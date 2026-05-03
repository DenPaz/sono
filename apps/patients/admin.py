from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .constants import AROUSAL_THRESHOLD
from .constants import EXCESSIVE_DAYTIME_SLEEPINESS_THRESHOLD
from .constants import HYPERHIDROSIS_THRESHOLD
from .constants import RESPIRATORY_THRESHOLD
from .constants import SLEEP_ONSET_MAINTENANCE_THRESHOLD
from .constants import SLEEP_WAKE_TRANSITION_THRESHOLD
from .models import Patient
from .models import QuestionnaireResponse


class QuestionnaireResponseInline(admin.TabularInline):
    model = QuestionnaireResponse
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    inlines = [QuestionnaireResponseInline]
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


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("Patient information"),
            {
                "fields": ("patient",),
            },
        ),
        (
            _("Questionnaire responses"),
            {
                "fields": (
                    "q1",
                    "q2",
                    "q3",
                    "q4",
                    "q5",
                    "q6",
                    "q7",
                    "q8",
                    "q9",
                    "q10",
                    "q11",
                    "q12",
                    "q13",
                    "q14",
                    "q15",
                    "q16",
                    "q17",
                    "q18",
                    "q19",
                    "q20",
                    "q21",
                    "q22",
                    "q23",
                    "q24",
                    "q25",
                    "q26",
                ),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("id", "created", "modified"),
            },
        ),
    )
    list_display = [
        "id",
        "patient",
        "created",
        "sleep_onset_maintenance_score",
        "respiratory_score",
        "arousal_score",
        "sleep_wake_transition_score",
        "excessive_daytime_sleepiness_score",
        "hyperhidrosis_score",
        "total_score",
    ]
    list_filter = [
        "patient__biological_sex",
    ]
    search_fields = [
        "patient__parent__first_name",
        "patient__parent__last_name",
        "patient__specialist__first_name",
        "patient__specialist__last_name",
    ]
    readonly_fields = [
        "id",
        "created",
        "modified",
    ]
    autocomplete_fields = [
        "patient",
    ]
    list_per_page = 20
    show_full_result_count = False

    @admin.display(description=_("Onset & maintenance"))
    def sleep_onset_maintenance_score(self, obj):
        score = obj.sleep_onset_maintenance_score
        threshold = SLEEP_ONSET_MAINTENANCE_THRESHOLD
        return f"{'⚠️' if score > threshold else '✓'} {score}/{threshold}"

    @admin.display(description=_("Respiratory"))
    def respiratory_score(self, obj):
        score = obj.respiratory_score
        threshold = RESPIRATORY_THRESHOLD
        return f"{'⚠️' if score > threshold else '✓'} {score}/{threshold}"

    @admin.display(description=_("Arousal"))
    def arousal_score(self, obj):
        score = obj.arousal_score
        threshold = AROUSAL_THRESHOLD
        return f"{'⚠️' if score > threshold else '✓'} {score}/{threshold}"

    @admin.display(description=_("Sleep-wake transition"))
    def sleep_wake_transition_score(self, obj):
        score = obj.sleep_wake_transition_score
        threshold = SLEEP_WAKE_TRANSITION_THRESHOLD
        return f"{'⚠️' if score > threshold else '✓'} {score}/{threshold}"

    @admin.display(description=_("Daytime sleepiness"))
    def excessive_daytime_sleepiness_score(self, obj):
        score = obj.excessive_daytime_sleepiness_score
        threshold = EXCESSIVE_DAYTIME_SLEEPINESS_THRESHOLD
        return f"{'⚠️' if score > threshold else '✓'} {score}/{threshold}"

    @admin.display(description=_("Hyperhidrosis"))
    def hyperhidrosis_score(self, obj):
        score = obj.hyperhidrosis_score
        threshold = HYPERHIDROSIS_THRESHOLD
        return f"{'⚠️' if score > threshold else '✓'} {score}/{threshold}"

    @admin.display(description=_("Total score"))
    def total_score(self, obj):
        return obj.total_score
