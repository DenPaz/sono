import pytest
from django.db import IntegrityError

from apps.users.enums import UserRole
from apps.users.tests.factories import AdminFactory
from apps.users.tests.factories import AdminProfileFactory
from apps.users.tests.factories import ParentFactory
from apps.users.tests.factories import ParentProfileFactory
from apps.users.tests.factories import SpecialistFactory
from apps.users.tests.factories import SpecialistProfileFactory
from apps.users.tests.factories import UserFactory
from apps.users.utils import get_default_avatar_url

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_email_field_is_unique(self):
        email = "john.doe@example.com"
        UserFactory(email=email)
        with pytest.raises(IntegrityError):
            UserFactory(email=email)

    def test_str_method_returns_full_name_and_email(self):
        user = UserFactory(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        expected_str = "John Doe <john.doe@example.com>"
        assert str(user) == expected_str

    def test_profile_property_returns_none_if_role_is_not_set(self):
        user = UserFactory(role="")
        assert user.profile is None


class TestAdminModel:
    def test_role_is_set_to_admin_by_default(self):
        admin = AdminFactory()
        assert admin.role == UserRole.ADMIN

    def test_is_staff_and_is_superuser_are_true_for_admin(self):
        admin = AdminFactory()
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_profile_property_returns_admin_profile(self):
        admin = AdminFactory()
        assert admin.profile == admin.admin_profile


class TestSpecialistModel:
    def test_role_is_set_to_specialist_by_default(self):
        specialist = SpecialistFactory()
        assert specialist.role == UserRole.SPECIALIST

    def test_is_staff_and_is_superuser_are_false_for_specialist(self):
        specialist = SpecialistFactory()
        assert specialist.is_staff is False
        assert specialist.is_superuser is False

    def test_profile_property_returns_specialist_profile(self):
        specialist = SpecialistFactory()
        assert specialist.profile == specialist.specialist_profile


class TestParentModel:
    def test_role_is_set_to_parent_by_default(self):
        parent = ParentFactory()
        assert parent.role == UserRole.PARENT

    def test_is_staff_and_is_superuser_are_false_for_parent(self):
        parent = ParentFactory()
        assert parent.is_staff is False
        assert parent.is_superuser is False

    def test_profile_property_returns_parent_profile(self):
        parent = ParentFactory()
        assert parent.profile == parent.parent_profile


class TestAdminProfileModel:
    def test_str_method_returns_user_str(self):
        admin_profile = AdminProfileFactory()
        expected_str = str(admin_profile.user)
        assert str(admin_profile) == expected_str

    def test_get_avatar_url_method_returns_default_avatar_url_if_no_avatar(self):
        admin_profile = AdminProfileFactory()
        assert admin_profile.get_avatar_url() == get_default_avatar_url()


class TestSpecialistProfileModel:
    def test_str_method_returns_user_str(self):
        specialist_profile = SpecialistProfileFactory()
        expected_str = str(specialist_profile.user)
        assert str(specialist_profile) == expected_str

    def test_get_avatar_url_method_returns_default_avatar_url_if_no_avatar(self):
        specialist_profile = SpecialistProfileFactory()
        assert specialist_profile.get_avatar_url() == get_default_avatar_url()


class TestParentProfileModel:
    def test_str_method_returns_user_str(self):
        parent_profile = ParentProfileFactory()
        expected_str = str(parent_profile.user)
        assert str(parent_profile) == expected_str

    def test_get_avatar_url_method_returns_default_avatar_url_if_no_avatar(self):
        parent_profile = ParentProfileFactory()
        assert parent_profile.get_avatar_url() == get_default_avatar_url()
