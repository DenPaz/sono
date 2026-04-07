from django.urls import path
from django.views.generic import RedirectView

from .views import SettingsView

app_name = "users"

urlpatterns = [
    path(
        route="login/",
        view=RedirectView.as_view(
            pattern_name="account_login",
            permanent=False,
            query_string=True,
        ),
        name="login",
    ),
    path(
        route="password-recovery/",
        view=RedirectView.as_view(
            pattern_name="account_reset_password",
            permanent=False,
            query_string=True,
        ),
        name="password_recovery",
    ),
    path(
        route="settings/",
        view=SettingsView.as_view(),
        name="settings",
    ),
]
