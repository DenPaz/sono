from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models

from apps.core.managers import ActiveQuerySet

from .enums import UserRole


class UserQuerySet(ActiveQuerySet):
    def with_profile(self):
        return self.select_related(
            "admin_profile",
            "specialist_profile",
            "parent_profile",
        )


class UserManager(DjangoUserManager.from_queryset(UserQuerySet)):
    role = None

    def _create_user(self, email, password, **extra_fields):
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        if self.role is not None:
            extra_fields.setdefault("role", self.role)
        if self.role == UserRole.ADMIN:
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_superuser", True)
        else:
            extra_fields.setdefault("is_staff", False)
            extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("role") != UserRole.ADMIN:
            msg = "Superuser must have role of Admin."
            raise ValueError(msg)
        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)
        return self._create_user(email, password, **extra_fields)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.role is not None:
            queryset = queryset.filter(role=self.role)
        return queryset


class AdminQuerySet(UserQuerySet):
    def with_profile(self):
        return self.select_related("admin_profile")


class AdminManager(UserManager.from_queryset(AdminQuerySet)):
    role = UserRole.ADMIN


class SpecialistQuerySet(UserQuerySet):
    def with_profile(self):
        return self.select_related("specialist_profile")


class SpecialistManager(UserManager.from_queryset(SpecialistQuerySet)):
    role = UserRole.SPECIALIST


class ParentQuerySet(UserQuerySet):
    def with_profile(self):
        return self.select_related("parent_profile")


class ParentManager(UserManager.from_queryset(ParentQuerySet)):
    role = UserRole.PARENT


class UserProfileQuerySet(models.QuerySet):
    def with_user(self):
        return self.select_related("user")


class UserProfileManager(models.Manager.from_queryset(UserProfileQuerySet)):
    pass


class AdminProfileQuerySet(UserProfileQuerySet):
    pass


class AdminProfileManager(UserProfileManager.from_queryset(AdminProfileQuerySet)):
    pass


class SpecialistProfileQuerySet(UserProfileQuerySet):
    pass


class SpecialistProfileManager(
    UserProfileManager.from_queryset(SpecialistProfileQuerySet)
):
    pass


class ParentProfileQuerySet(UserProfileQuerySet):
    pass


class ParentProfileManager(UserProfileManager.from_queryset(ParentProfileQuerySet)):
    pass
