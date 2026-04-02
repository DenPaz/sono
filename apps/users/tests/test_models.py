import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.users.utils import get_default_avatar_url

from .factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_str_method_returns_full_name_and_email(self):
        """
        Test the __str__ method returns the full name and email in the format
        "First Last <email>"
        """
        user = UserFactory(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        expected_str = "John Doe <john.doe@example.com>"
        assert str(user) == expected_str

    def test_email_field_is_unique(self):
        """
        Test that the email field is unique and raises an IntegrityError when
        trying to create a user with an email that already exists.
        """
        UserFactory(email="test@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="test@example.com")


@pytest.mark.django_db
class TestUserProfileModel:
    def test_str_method_returns_user_str(self):
        """
        Test the __str__ method of UserProfile returns the string representation of
        the associated User, which includes the full name and email.
        """
        user = UserFactory(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
        )
        expected_str = "Jane Smith <jane.smith@example.com>"
        assert str(user.profile) == expected_str

    def test_get_avatar_url_method_returns_default_avatar_url_when_no_avatar(self):
        """
        Test that the get_avatar_url method of UserProfile returns the default avatar
        URL when the user does not have an avatar set.
        """
        profile = UserFactory().profile
        expected_url = get_default_avatar_url()
        assert profile.get_avatar_url() == expected_url
