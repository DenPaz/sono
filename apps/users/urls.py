from django.urls import path

from .views import AdminCreateView
from .views import AdminUpdateView
from .views import ParentCreateView
from .views import ParentListView
from .views import ParentUpdateView
from .views import ProfileView
from .views import SettingsView
from .views import SpecialistCreateView
from .views import SpecialistUpdateView
from .views import UserListView

app_name = "users"

urlpatterns = [
    path(
        route="",
        view=UserListView.as_view(),
        name="user_list",
    ),
    path(
        route="profile/",
        view=ProfileView.as_view(),
        name="profile",
    ),
    path(
        route="settings/",
        view=SettingsView.as_view(),
        name="settings",
    ),
    path(
        route="admins/create/",
        view=AdminCreateView.as_view(),
        name="admin_create",
    ),
    path(
        route="admins/<uuid:pk>/update/",
        view=AdminUpdateView.as_view(),
        name="admin_update",
    ),
    path(
        route="specialists/create/",
        view=SpecialistCreateView.as_view(),
        name="specialist_create",
    ),
    path(
        route="specialists/<uuid:pk>/update/",
        view=SpecialistUpdateView.as_view(),
        name="specialist_update",
    ),
    path(
        route="parents/",
        view=ParentListView.as_view(),
        name="parent_list",
    ),
    path(
        route="parents/create/",
        view=ParentCreateView.as_view(),
        name="parent_create",
    ),
    path(
        route="parents/<uuid:pk>/update/",
        view=ParentUpdateView.as_view(),
        name="parent_update",
    ),
]
