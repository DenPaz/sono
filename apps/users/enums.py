from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    SPECIALIST = "SPECIALIST", _("Specialist")
    PARENT = "PARENT", _("Parent")
