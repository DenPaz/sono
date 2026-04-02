import pytest

from .factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_profile_created_on_user_creation():
    """
    Test that a UserProfile is automatically created when a new User is created.
    """
    user = UserFactory()
    assert hasattr(user, "profile")
    assert user.profile.user == user
