import pytest
from django.contrib.auth.models import Group

from apps.users.enums import UserRole
from apps.users.models import AdminProfile
from apps.users.models import ParentProfile
from apps.users.models import SpecialistProfile
from apps.users.tests.factories import AdminFactory
from apps.users.tests.factories import ParentFactory
from apps.users.tests.factories import SpecialistFactory
from apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCreateUserGroupsSignal:
    def test_admin_group_exists(self):
        assert Group.objects.filter(name=UserRole.ADMIN).exists()

    def test_specialist_group_exists(self):
        assert Group.objects.filter(name=UserRole.SPECIALIST).exists()

    def test_parent_group_exists(self):
        assert Group.objects.filter(name=UserRole.PARENT).exists()

    def test_all_groups_exist(self):
        expected_groups = set(UserRole.values)
        actual_groups = set(
            Group.objects.filter(name__in=UserRole.values).values_list(
                "name", flat=True
            )
        )
        assert expected_groups == actual_groups


class TestCreateUserProfileSignal:
    def test_admin_profile_created_on_admin_save(self):
        admin = AdminFactory()
        assert AdminProfile.objects.filter(user=admin).exists()

    def test_admin_is_added_to_admin_group(self):
        admin = AdminFactory()
        assert admin.groups.filter(name=UserRole.ADMIN).exists()

    def test_specialist_profile_created_on_specialist_save(self):
        specialist = SpecialistFactory()
        assert SpecialistProfile.objects.filter(user=specialist).exists()

    def test_specialist_is_added_to_specialist_group(self):
        specialist = SpecialistFactory()
        assert specialist.groups.filter(name=UserRole.SPECIALIST).exists()

    def test_parent_profile_created_on_parent_save(self):
        parent = ParentFactory()
        assert ParentProfile.objects.filter(user=parent).exists()

    def test_parent_is_added_to_parent_group(self):
        parent = ParentFactory()
        assert parent.groups.filter(name=UserRole.PARENT).exists()

    def test_profile_created_on_user_save_with_role(self):
        user = UserFactory(role=UserRole.PARENT)
        assert ParentProfile.objects.filter(user=user).exists()

    def test_user_is_added_to_group_on_user_save_with_role(self):
        user = UserFactory(role=UserRole.SPECIALIST)
        assert user.groups.filter(name=UserRole.SPECIALIST).exists()
