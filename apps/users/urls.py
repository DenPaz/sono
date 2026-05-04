from django.urls import path

from .views import AdminCreateView
from .views import AdminUpdateView
from .views import ParentListView
from .views import UserListView

app_name = "users"

urlpatterns = [
    path(
        route="",
        view=UserListView.as_view(),
        name="user_list",
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
        route="parents/",
        view=ParentListView.as_view(),
        name="parent_list",
    ),
]
