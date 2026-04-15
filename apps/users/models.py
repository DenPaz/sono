from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.core.validators import FileSizeValidator

from .managers import UserManager
from .managers import UserProfileManager
from .utils import get_default_avatar_url
from .utils import get_user_upload_path


class User(BaseModel, AbstractUser):
    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=150,
    )
    email = models.EmailField(
        verbose_name=_("Email address"),
        unique=True,
    )
    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"


class UserProfile(BaseModel):
    user = models.OneToOneField(
        to=User,
        verbose_name=_("User"),
        related_name="profile",
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to=get_user_upload_path,
        validators=[
            FileSizeValidator(max_size=5, unit="MB"),
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
        ],
        blank=True,
        help_text=_("Maximum size: 5MB. Allowed formats: .jpg, .jpeg, .png"),
    )
    language = models.CharField(
        verbose_name=_("Language"),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
    )
    timezone = models.CharField(
        verbose_name=_("Timezone"),
        max_length=100,
        default=settings.TIME_ZONE,
    )

    objects = UserProfileManager()

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self):
        return f"{self.user}"

    def get_avatar_url(self) -> str:
        """Return the avatar image URL or a default one if not set."""
        if self.avatar:
            return self.avatar.url
        return get_default_avatar_url()
