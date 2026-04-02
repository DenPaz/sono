from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms_admin import UserAdminChangeForm
from .forms_admin import UserAdminCreationForm
from .models import User
from .models import UserProfile

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    min_num = 1
    max_num = 1

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.with_user()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    inlines = [UserProfileInline]
    fieldsets = (
        (
            _("Account information"),
            {
                "fields": (
                    "id",
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                    "is_active",
                    "last_login",
                    "date_joined",
                ),
            },
        ),
        (
            _("Permissions"),
            {
                "classes": ("collapse",),
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            _("Account information"),
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                ),
            },
        ),
    )
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    filter_horizontal = [
        "user_permissions",
        "groups",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "email",
    ]
    ordering = [
        "first_name",
        "last_name",
    ]
    readonly_fields = [
        "id",
        "last_login",
        "date_joined",
    ]
    list_per_page = 20
    show_full_result_count = False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.with_profile()
