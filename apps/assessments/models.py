from __future__ import annotations

import base64
import hashlib
import hmac

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.assessments import constants
from apps.core.managers import ActiveQuerySet
from apps.core.models import BaseModel


def normalize_child_name(value: str) -> str:
    return " ".join(str(value or "").strip().split())


def _build_child_name_cipher() -> Fernet:
    encryption_key = getattr(settings, "ASSESSMENTS_CHILD_NAME_ENCRYPTION_KEY", "")
    if not encryption_key:
        msg = "ASSESSMENTS_CHILD_NAME_ENCRYPTION_KEY is required."
        raise ValueError(msg)

    derived_key = hashlib.sha256(encryption_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(derived_key))


def encrypt_child_name(value: str) -> str:
    normalized = normalize_child_name(value)
    if not normalized:
        return ""
    encrypted = _build_child_name_cipher().encrypt(normalized.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_child_name(value: str) -> str:
    encrypted_value = str(value or "").strip()
    if not encrypted_value:
        return ""

    try:
        decrypted = _build_child_name_cipher().decrypt(encrypted_value.encode("utf-8"))
    except InvalidToken as exc:
        msg = "Invalid encrypted child name token."
        raise ValueError(msg) from exc

    return decrypted.decode("utf-8")


def compute_child_name_blind_index(value: str) -> str:
    normalized = normalize_child_name(value)
    if not normalized:
        return ""

    blind_index_key = getattr(settings, "ASSESSMENTS_CHILD_NAME_BLIND_INDEX_KEY", "")
    if not blind_index_key:
        msg = "ASSESSMENTS_CHILD_NAME_BLIND_INDEX_KEY is required."
        raise ValueError(msg)

    return hmac.new(
        blind_index_key.encode("utf-8"),
        normalized.casefold().encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class MunicipalityQuerySet(ActiveQuerySet):
    pass


class Municipality(BaseModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    state_code = models.CharField(
        verbose_name=_("State code"),
        max_length=2,
    )
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )

    objects = MunicipalityQuerySet.as_manager()

    class Meta:
        verbose_name = _("Municipality")
        verbose_name_plural = _("Municipalities")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "state_code"],
                name="uq_municipality_name_state_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}/{self.state_code}"


class ProfessionalProfileQuerySet(ActiveQuerySet):
    pass


class ProfessionalProfile(BaseModel):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        related_name="assessments_profile",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    municipality = models.ForeignKey(
        to=Municipality,
        related_name="professionals",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Municipality"),
    )
    registration_code = models.CharField(
        verbose_name=_("Registration code"),
        max_length=64,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )

    objects = ProfessionalProfileQuerySet.as_manager()

    class Meta:
        verbose_name = _("Professional profile")
        verbose_name_plural = _("Professional profiles")
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self) -> str:
        return f"{self.user.get_full_name()}"


class AssessmentEvaluationQuerySet(ActiveQuerySet):
    def drafts(self):
        return self.filter(status=constants.EVALUATION_STATUS_DRAFT)

    def completed(self):
        return self.filter(
            status__in=(
                constants.EVALUATION_STATUS_COMPLETED,
                constants.EVALUATION_STATUS_REVIEWED,
            )
        )

    def visible_for_user(self, *, user, can_view_all_assessments: bool):
        if user.is_superuser or can_view_all_assessments:
            return self
        return self.filter(professional=user)


class AssessmentEvaluation(BaseModel):
    professional = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="assessments",
        on_delete=models.PROTECT,
        verbose_name=_("Professional"),
    )
    municipality = models.ForeignKey(
        to=Municipality,
        related_name="assessments",
        on_delete=models.PROTECT,
        verbose_name=_("Municipality"),
    )
    child_name = models.CharField(
        verbose_name=_("Child name"),
        max_length=255,
        blank=True,
        default="",
    )
    child_name_encrypted = models.TextField(
        verbose_name=_("Child name encrypted"),
        blank=True,
        default="",
    )
    child_name_blind_index = models.CharField(
        verbose_name=_("Child name blind index"),
        max_length=64,
        blank=True,
        default="",
        db_index=True,
    )
    child_age = models.PositiveSmallIntegerField(
        verbose_name=_("Child age"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(18)],
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=constants.EVALUATION_STATUS_CHOICES,
        default=constants.EVALUATION_STATUS_DRAFT,
        db_index=True,
    )
    current_step = models.PositiveSmallIntegerField(
        verbose_name=_("Current step"),
        default=constants.WIZARD_IDENTIFICATION_STEP,
    )
    answers = models.JSONField(
        verbose_name=_("Answers"),
        default=dict,
        blank=True,
    )
    total_score = models.PositiveSmallIntegerField(
        verbose_name=_("Total score"),
        null=True,
        blank=True,
    )
    alert_count = models.PositiveSmallIntegerField(
        verbose_name=_("Alert count"),
        null=True,
        blank=True,
    )
    risk_level = models.CharField(
        verbose_name=_("Risk level"),
        max_length=20,
        choices=constants.RISK_LEVEL_CHOICES,
        default=constants.RISK_LEVEL_NO_ALERT,
        db_index=True,
    )
    subscale_scores = models.JSONField(
        verbose_name=_("Subscale scores"),
        default=dict,
        blank=True,
    )
    completed_at = models.DateTimeField(
        verbose_name=_("Completed at"),
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="assessments_reviewed",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Reviewed by"),
    )
    reviewed_at = models.DateTimeField(
        verbose_name=_("Reviewed at"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )

    objects = AssessmentEvaluationQuerySet.as_manager()

    class Meta:
        verbose_name = _("Assessment evaluation")
        verbose_name_plural = _("Assessment evaluations")
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["professional"],
                condition=Q(
                    status=constants.EVALUATION_STATUS_DRAFT,
                    is_active=True,
                ),
                name="uq_active_draft_per_professional",
            )
        ]

    def __str__(self) -> str:
        return f"Avaliação {self.id}"

    def save(self, *args, **kwargs):
        # Ensure plaintext names are never persisted in the legacy column.
        normalized_child_name = normalize_child_name(self.child_name)
        if normalized_child_name:
            self.set_child_name(normalized_child_name)
        elif self.child_name:
            self.child_name = ""

        super().save(*args, **kwargs)

    def set_child_name(self, value: str) -> None:
        normalized = normalize_child_name(value)
        if not normalized:
            msg = _("Nome da criança é obrigatório.")
            raise ValueError(str(msg))

        self.child_name_encrypted = encrypt_child_name(normalized)
        self.child_name_blind_index = compute_child_name_blind_index(normalized)
        # Legacy plaintext column kept empty until the drop migration.
        self.child_name = ""

    def get_child_name(self) -> str:
        if self.child_name_encrypted:
            try:
                return decrypt_child_name(self.child_name_encrypted)
            except ValueError:
                return ""
        return normalize_child_name(self.child_name)

    def get_child_reference(self) -> str:
        blind_index = str(self.child_name_blind_index or "").strip().lower()
        if not blind_index:
            child_name = self.get_child_name()
            if child_name:
                blind_index = compute_child_name_blind_index(child_name)

        if blind_index:
            return f"CR-{blind_index[:10].upper()}"

        evaluation_id = str(self.id).split("-")[0].upper() if self.id else "SEM-ID"
        return f"CR-{evaluation_id}"

    @property
    def total_answered(self) -> int:
        return len(self.answers)

    def mark_completed(
        self,
        *,
        total_score: int,
        alert_count: int,
        risk_level: str,
        subscale_scores: dict,
    ) -> None:
        self.status = constants.EVALUATION_STATUS_COMPLETED
        self.total_score = total_score
        self.alert_count = alert_count
        self.risk_level = risk_level
        self.subscale_scores = subscale_scores
        self.completed_at = timezone.now()
        self.current_step = constants.WIZARD_TOTAL_STEPS - 1

    def mark_reviewed(self, *, reviewer) -> None:
        self.status = constants.EVALUATION_STATUS_REVIEWED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()


INVITE_STATUS_PENDING = "pending"
INVITE_STATUS_ACCEPTED = "accepted"
INVITE_STATUS_EXPIRED = "expired"

INVITE_STATUS_CHOICES = (
    (INVITE_STATUS_PENDING, _("Pending")),
    (INVITE_STATUS_ACCEPTED, _("Accepted")),
    (INVITE_STATUS_EXPIRED, _("Expired")),
)


class ProfessionalInvite(BaseModel):
    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=150,
    )
    email = models.EmailField(
        verbose_name=_("Email"),
    )
    municipality = models.ForeignKey(
        to=Municipality,
        related_name="invites",
        on_delete=models.PROTECT,
        verbose_name=_("Municipality"),
        null=True,
        blank=True,
    )
    invited_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="professional_invites",
        on_delete=models.PROTECT,
        verbose_name=_("Invited by"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=INVITE_STATUS_CHOICES,
        default=INVITE_STATUS_PENDING,
    )

    class Meta:
        verbose_name = _("Professional invite")
        verbose_name_plural = _("Professional invites")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.email}>"
