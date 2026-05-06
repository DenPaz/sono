from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_fields.fields import EncryptedCharField
from encrypted_fields.fields import EncryptedDateField
from encrypted_fields.fields import EncryptedTextField

from apps.core.models import BaseModel
from apps.users.models import Parent
from apps.users.models import Specialist

from .constants import AROUSAL_THRESHOLD
from .constants import EXCESSIVE_DAYTIME_SLEEPINESS_THRESHOLD
from .constants import HYPERHIDROSIS_THRESHOLD
from .constants import RESPIRATORY_THRESHOLD
from .constants import SLEEP_ONSET_MAINTENANCE_THRESHOLD
from .constants import SLEEP_WAKE_TRANSITION_THRESHOLD
from .enums import BiologicalSex
from .enums import QuestionnaireFrequency
from .enums import SleepDuration
from .enums import SleepOnsetDelay
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
        return f"{self.get_full_name()}"

    @property
    def age(self) -> int:
        today = timezone.localdate()
        birth_date = self.birth_date
        return (today.year - birth_date.year) - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self) -> str:
        return reverse("patients:patient_detail", kwargs={"pk": self.pk})


class QuestionnaireResponse(BaseModel):
    patient = models.ForeignKey(
        to=Patient,
        verbose_name=_("Patient"),
        related_name="questionnaire_responses",
        on_delete=models.PROTECT,
    )
    q1 = models.PositiveSmallIntegerField(
        verbose_name=_("Q1"),
        choices=SleepDuration.choices,
    )
    q2 = models.PositiveSmallIntegerField(
        verbose_name=_("Q2"),
        choices=SleepOnsetDelay.choices,
    )
    q3 = models.PositiveSmallIntegerField(
        verbose_name=_("Q3"),
        choices=QuestionnaireFrequency.choices,
    )
    q4 = models.PositiveSmallIntegerField(
        verbose_name=_("Q4"),
        choices=QuestionnaireFrequency.choices,
    )
    q5 = models.PositiveSmallIntegerField(
        verbose_name=_("Q5"),
        choices=QuestionnaireFrequency.choices,
    )
    q6 = models.PositiveSmallIntegerField(
        verbose_name=_("Q6"),
        choices=QuestionnaireFrequency.choices,
    )
    q7 = models.PositiveSmallIntegerField(
        verbose_name=_("Q7"),
        choices=QuestionnaireFrequency.choices,
    )
    q8 = models.PositiveSmallIntegerField(
        verbose_name=_("Q8"),
        choices=QuestionnaireFrequency.choices,
    )
    q9 = models.PositiveSmallIntegerField(
        verbose_name=_("Q9"),
        choices=QuestionnaireFrequency.choices,
    )
    q10 = models.PositiveSmallIntegerField(
        verbose_name=_("Q10"),
        choices=QuestionnaireFrequency.choices,
    )
    q11 = models.PositiveSmallIntegerField(
        verbose_name=_("Q11"),
        choices=QuestionnaireFrequency.choices,
    )
    q12 = models.PositiveSmallIntegerField(
        verbose_name=_("Q12"),
        choices=QuestionnaireFrequency.choices,
    )
    q13 = models.PositiveSmallIntegerField(
        verbose_name=_("Q13"),
        choices=QuestionnaireFrequency.choices,
    )
    q14 = models.PositiveSmallIntegerField(
        verbose_name=_("Q14"),
        choices=QuestionnaireFrequency.choices,
    )
    q15 = models.PositiveSmallIntegerField(
        verbose_name=_("Q15"),
        choices=QuestionnaireFrequency.choices,
    )
    q16 = models.PositiveSmallIntegerField(
        verbose_name=_("Q16"),
        choices=QuestionnaireFrequency.choices,
    )
    q17 = models.PositiveSmallIntegerField(
        verbose_name=_("Q17"),
        choices=QuestionnaireFrequency.choices,
    )
    q18 = models.PositiveSmallIntegerField(
        verbose_name=_("Q18"),
        choices=QuestionnaireFrequency.choices,
    )
    q19 = models.PositiveSmallIntegerField(
        verbose_name=_("Q19"),
        choices=QuestionnaireFrequency.choices,
    )
    q20 = models.PositiveSmallIntegerField(
        verbose_name=_("Q20"),
        choices=QuestionnaireFrequency.choices,
    )
    q21 = models.PositiveSmallIntegerField(
        verbose_name=_("Q21"),
        choices=QuestionnaireFrequency.choices,
    )
    q22 = models.PositiveSmallIntegerField(
        verbose_name=_("Q22"),
        choices=QuestionnaireFrequency.choices,
    )
    q23 = models.PositiveSmallIntegerField(
        verbose_name=_("Q23"),
        choices=QuestionnaireFrequency.choices,
    )
    q24 = models.PositiveSmallIntegerField(
        verbose_name=_("Q24"),
        choices=QuestionnaireFrequency.choices,
    )
    q25 = models.PositiveSmallIntegerField(
        verbose_name=_("Q25"),
        choices=QuestionnaireFrequency.choices,
    )
    q26 = models.PositiveSmallIntegerField(
        verbose_name=_("Q26"),
        choices=QuestionnaireFrequency.choices,
    )

    class Meta:
        verbose_name = _("Questionnaire response")
        verbose_name_plural = _("Questionnaire responses")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.id} ({self.created.strftime('%d/%m/%Y')})"

    @property
    def sleep_onset_maintenance_score(self) -> int:
        return self.q1 + self.q2 + self.q3 + self.q4 + self.q5 + self.q10 + self.q11

    @property
    def respiratory_score(self) -> int:
        return self.q13 + self.q14 + self.q15

    @property
    def arousal_score(self) -> int:
        return self.q17 + self.q20 + self.q21

    @property
    def sleep_wake_transition_score(self) -> int:
        return self.q6 + self.q7 + self.q8 + self.q12 + self.q18 + self.q19

    @property
    def excessive_daytime_sleepiness_score(self) -> int:
        return self.q22 + self.q23 + self.q24 + self.q25 + self.q26

    @property
    def hyperhidrosis_score(self) -> int:
        return self.q9 + self.q16

    @property
    def total_score(self) -> int:
        return (
            self.sleep_onset_maintenance_score
            + self.respiratory_score
            + self.arousal_score
            + self.sleep_wake_transition_score
            + self.excessive_daytime_sleepiness_score
            + self.hyperhidrosis_score
        )

    @property
    def flags(self) -> dict[str, bool]:
        return {
            "sleep_onset_maintenance": self.sleep_onset_maintenance_score
            > SLEEP_ONSET_MAINTENANCE_THRESHOLD,
            "respiratory": self.respiratory_score > RESPIRATORY_THRESHOLD,
            "arousal": self.arousal_score > AROUSAL_THRESHOLD,
            "sleep_wake_transition": self.sleep_wake_transition_score
            > SLEEP_WAKE_TRANSITION_THRESHOLD,
            "excessive_daytime_sleepiness": self.excessive_daytime_sleepiness_score
            > EXCESSIVE_DAYTIME_SLEEPINESS_THRESHOLD,
            "hyperhidrosis": self.hyperhidrosis_score > HYPERHIDROSIS_THRESHOLD,
        }

    @property
    def has_flags(self) -> bool:
        return any(self.flags.values())
