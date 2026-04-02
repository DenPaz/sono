from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UppercaseValidator:
    """Validate that the password contains at least one uppercase letter."""

    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                self.get_error_message(),
                code="password_no_upper",
            )

    def get_error_message(self):
        return _("This password does not contain an uppercase letter.")

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")


class LowercaseValidator:
    """Validate that the password contains at least one lowercase letter."""

    def validate(self, password, user=None):
        if not any(char.islower() for char in password):
            raise ValidationError(
                self.get_error_message(),
                code="password_no_lower",
            )

    def get_error_message(self):
        return _("This password does not contain a lowercase letter.")

    def get_help_text(self):
        return _("Your password must contain at least one lowercase letter.")
