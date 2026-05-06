from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", _("Administrador")
    SPECIALIST = "SPECIALIST", _("Especialista")
    PARENT = "PARENT", _("Responsável")
