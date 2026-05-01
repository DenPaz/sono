from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms_admin import AdminAdminChangeForm
from .forms_admin import AdminAdminCreationForm
from .forms_admin import ParentAdminChangeForm
from .forms_admin import ParentAdminCreationForm
from .forms_admin import SpecialistAdminChangeForm
from .forms_admin import SpecialistAdminCreationForm
from .forms_admin import UserAdminChangeForm
from .forms_admin import UserAdminCreationForm
from .models import Admin
from .models import AdminProfile
from .models import Parent
from .models import ParentProfile
from .models import Specialist
from .models import SpecialistProfile
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (
            _("Account information"),
            {
                "fields": (
                    "id",
                    "first_name",
                    "last_name",
                    "email",
                    "role",
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
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
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
                    "role",
                ),
            },
        ),
    )
    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    list_filter = [
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    filter_horizontal = [
        "groups",
        "user_permissions",
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


class UserProfileInline(admin.StackedInline):
    can_delete = False
    min_num = 1
    max_num = 1
    readonly_fields = ["timezone"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.with_user()


class AdminProfileInline(UserProfileInline):
    model = AdminProfile


@admin.register(Admin)
class AdminAdmin(UserAdmin):
    form = AdminAdminChangeForm
    add_form = AdminAdminCreationForm
    inlines = [AdminProfileInline]
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
    ]
    list_filter = [
        "is_active",
    ]


class SpecialistProfileInline(UserProfileInline):
    model = SpecialistProfile


@admin.register(Specialist)
class SpecialistAdmin(UserAdmin):
    form = SpecialistAdminChangeForm
    add_form = SpecialistAdminCreationForm
    inlines = [SpecialistProfileInline]
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
    ]
    list_filter = [
        "is_active",
    ]


class ParentProfileInline(UserProfileInline):
    model = ParentProfile


@admin.register(Parent)
class ParentAdmin(UserAdmin):
    form = ParentAdminChangeForm
    add_form = ParentAdminCreationForm
    inlines = [ParentProfileInline]
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
    ]
    list_filter = [
        "is_active",
    ]
