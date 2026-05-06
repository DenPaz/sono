from http import HTTPStatus

import pytest
from django.core import mail
from django.urls import reverse

from apps.patients.tests.factories import PatientFactory
from apps.users.models import Specialist
from apps.users.tests.factories import AdminFactory
from apps.users.tests.factories import SpecialistFactory

pytestmark = pytest.mark.django_db


class TestDashboardViews:
    def test_index_renders_for_admin(self, client):
        admin = AdminFactory()

        client.force_login(admin)
        response = client.get(reverse("dashboard:index"))

        assert response.status_code == HTTPStatus.OK

    def test_invite_professional_creates_specialist_and_sends_email(self, client):
        admin = AdminFactory()

        client.force_login(admin)
        response = client.post(
            reverse("dashboard:invite_professional"),
            data={
                "name": "Camila Rocha",
                "email": "camila.rocha@example.com",
            },
            follow=True,
        )

        assert response.status_code == HTTPStatus.OK
        specialist = Specialist.objects.get(email="camila.rocha@example.com")
        assert specialist.first_name == "Camila"
        assert specialist.last_name == "Rocha"
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["camila.rocha@example.com"]

    def test_manage_professional_updates_name_and_status(self, client):
        admin = AdminFactory()
        specialist = SpecialistFactory(first_name="Bruno", last_name="Silva")

        client.force_login(admin)
        response = client.post(
            reverse("dashboard:manage_professional"),
            data={
                "email": specialist.email,
                "name": "Bruna Costa",
                "status": "inactive",
            },
            follow=True,
        )

        specialist.refresh_from_db()

        assert response.status_code == HTTPStatus.OK
        assert specialist.first_name == "Bruna"
        assert specialist.last_name == "Costa"
        assert specialist.is_active is False

    def test_professionals_page_includes_invited_specialists(self, client):
        admin = AdminFactory()
        specialist = SpecialistFactory(
            first_name="Maria",
            last_name="Oliveira",
            email="maria.oliveira@example.com",
        )
        PatientFactory(specialist=specialist)

        client.force_login(admin)
        response = client.get(reverse("dashboard:professionals"))

        assert response.status_code == HTTPStatus.OK
        assert "maria.oliveira@example.com" in response.content.decode()
