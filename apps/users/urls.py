from django.urls import path

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
        route="parents/",
        view=ParentListView.as_view(),
        name="parent_list",
    ),
]
