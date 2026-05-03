from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_fields.fields import EncryptedCharField
from encrypted_fields.fields import EncryptedDateField
from encrypted_fields.fields import EncryptedTextField

from apps.core.models import BaseModel
from apps.users.models import Parent
from apps.users.models import Specialist

from .enums import BiologicalSex
from .managers import PatientManager


class Patient(BaseModel):
    first_name = EncryptedCharField(
        verbose_name=_("First name"),
        max_length=100,
    )
    last_name = EncryptedCharField(
        verbose_name=_("Last name"),
        max_length=100,
    )
    birth_date = EncryptedDateField(
        verbose_name=_("Birth date"),
    )
    biological_sex = models.CharField(
        verbose_name=_("Biological sex"),
        max_length=2,
        choices=BiologicalSex.choices,
    )
    notes = EncryptedTextField(
        verbose_name=_("Notes"),
        default="",
        blank=True,
    )
    parent = models.ForeignKey(
        to=Parent,
        verbose_name=_("Parent"),
        related_name="patients",
        on_delete=models.PROTECT,
    )
    specialist = models.ForeignKey(
        to=Specialist,
        verbose_name=_("Specialist"),
        related_name="specialist_patients",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
    )

    objects = PatientManager()

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        today = timezone.localdate()
        birth_date = self.birth_date
        return (today.year - birth_date.year) - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
