from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views

from apps.users.views import SetLanguageView

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("i18n/set-language/", SetLanguageView.as_view(), name="set_language"),
    path("accounts/", include("allauth.urls")),
    path("", include("apps.dashboard.urls", namespace="dashboard")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("patients/", include("apps.patients.urls", namespace="patients")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path(
            route="400/",
            view=default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            route="403/",
            view=default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            route="404/",
            view=default_views.page_not_found,
            kwargs={"exception": Exception("Page Not Found")},
        ),
        path(
            route="500/",
            view=default_views.server_error,
        ),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
