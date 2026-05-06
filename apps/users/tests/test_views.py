from http import HTTPStatus

import pytest
from django.urls import reverse

from apps.patients.tests.factories import PatientFactory
from apps.users.tests.factories import AdminFactory
from apps.users.tests.factories import ParentFactory
from apps.users.tests.factories import SpecialistFactory

pytestmark = pytest.mark.django_db


class TestSettingsView:
    def test_admin_settings_persist_account_password_and_preferences(self, client):
        admin = AdminFactory(email="admin@example.com")

        client.force_login(admin)
        response = client.post(
            reverse("users:settings"),
            data={
                "first_name": "Config",
                "last_name": "Admin",
                "email": "config.admin@example.com",
                "new_password": "SenhaNova123!",
                "confirm_password": "SenhaNova123!",
                "email_alerts": "on",
                "lgpd_data_export": "on",
            },
            follow=True,
        )

        admin.refresh_from_db()

        assert response.status_code == HTTPStatus.OK
        assert admin.first_name == "Config"
        assert admin.last_name == "Admin"
        assert admin.email == "config.admin@example.com"
        assert admin.check_password("SenhaNova123!")
        assert admin.password_changed_at is not None
        assert admin.preferences == {
            "email_alerts": True,
            "weekly_report": False,
            "lgpd_data_export": True,
        }


class TestParentListView:
    def test_specialist_can_view_only_linked_parents(self, client):
        specialist = SpecialistFactory()
        other_specialist = SpecialistFactory()
        visible_parent = ParentFactory()
        hidden_parent = ParentFactory()

        PatientFactory(parent=visible_parent, specialist=specialist)
        PatientFactory(parent=hidden_parent, specialist=other_specialist)

        client.force_login(specialist)
        response = client.get(reverse("users:parent_list"))

        parents = list(response.context["parents"])

        assert response.status_code == HTTPStatus.OK
        assert visible_parent in parents
        assert hidden_parent not in parents

    def test_parent_list_denies_parent_role(self, client):
        parent = ParentFactory()

        client.force_login(parent)
        response = client.get(reverse("users:parent_list"))

        assert response.status_code == HTTPStatus.FORBIDDEN
