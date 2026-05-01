from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.core.validators import FileSizeValidator

from .enums import UserRole
from .managers import AdminManager
from .managers import AdminProfileManager
from .managers import ParentManager
from .managers import ParentProfileManager
from .managers import SpecialistManager
from .managers import SpecialistProfileManager
from .managers import UserManager
from .utils import get_default_avatar_url
from .utils import get_user_upload_path


class User(BaseModel, AbstractUser):
    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=100,
    )
    email = models.EmailField(
        verbose_name=_("Email address"),
        unique=True,
    )
    role = models.CharField(
        verbose_name=_("Role"),
        max_length=20,
        choices=UserRole.choices,
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

    @property
    def profile(self):
        if not self.role:
            return None
        return getattr(self, f"{self.role.lower()}_profile", None)


class Admin(User):
    objects = AdminManager()

    class Meta:
        proxy = True
        verbose_name = _("Admin")
        verbose_name_plural = _("Admins")
        ordering = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        self.role = UserRole.ADMIN
        self.is_staff = True
        self.is_superuser = True
        super().save(*args, **kwargs)


class Specialist(User):
    objects = SpecialistManager()

    class Meta:
        proxy = True
        verbose_name = _("Specialist")
        verbose_name_plural = _("Specialists")
        ordering = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        self.role = UserRole.SPECIALIST
        self.is_staff = False
        self.is_superuser = False
        super().save(*args, **kwargs)


class Parent(User):
    objects = ParentManager()

    class Meta:
        proxy = True
        verbose_name = _("Parent")
        verbose_name_plural = _("Parents")
        ordering = ["first_name", "last_name"]

    def save(self, *args, **kwargs):
        self.role = UserRole.PARENT
        self.is_staff = False
        self.is_superuser = False
        super().save(*args, **kwargs)


class UserProfile(BaseModel):
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

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return get_default_avatar_url()


class AdminProfile(UserProfile):
    user = models.OneToOneField(
        to=Admin,
        verbose_name=_("Admin"),
        related_name="admin_profile",
        on_delete=models.CASCADE,
    )

    objects = AdminProfileManager()

    class Meta:
        verbose_name = _("Admin profile")
        verbose_name_plural = _("Admin profiles")
        ordering = ["user__first_name", "user__last_name"]


class SpecialistProfile(UserProfile):
    user = models.OneToOneField(
        to=Specialist,
        verbose_name=_("Specialist"),
        related_name="specialist_profile",
        on_delete=models.CASCADE,
    )

    objects = SpecialistProfileManager()

    class Meta:
        verbose_name = _("Specialist profile")
        verbose_name_plural = _("Specialist profiles")
        ordering = ["user__first_name", "user__last_name"]


class ParentProfile(UserProfile):
    user = models.OneToOneField(
        to=Parent,
        verbose_name=_("Parent"),
        related_name="parent_profile",
        on_delete=models.CASCADE,
    )

    objects = ParentProfileManager()

    class Meta:
        verbose_name = _("Parent profile")
        verbose_name_plural = _("Parent profiles")
        ordering = ["user__first_name", "user__last_name"]
