# Generated manually for assessments app initial schema.

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Municipality",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Name"),
                ),
                (
                    "state_code",
                    models.CharField(max_length=2, verbose_name="State code"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active"),
                ),
            ],
            options={
                "verbose_name": "Municipality",
                "verbose_name_plural": "Municipalities",
                "ordering": ["name"],
                "unique_together": {("name", "state_code")},
            },
        ),
        migrations.CreateModel(
            name="AssessmentEvaluation",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "child_name",
                    models.CharField(max_length=255, verbose_name="Child name"),
                ),
                (
                    "child_age",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Child age",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("rascunho", "Rascunho"),
                            ("concluida", "Concluída"),
                            ("revisada", "Revisada"),
                        ],
                        db_index=True,
                        default="rascunho",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "current_step",
                    models.PositiveSmallIntegerField(default=0, verbose_name="Current step"),
                ),
                (
                    "answers",
                    models.JSONField(blank=True, default=dict, verbose_name="Answers"),
                ),
                (
                    "total_score",
                    models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Total score"),
                ),
                (
                    "alert_count",
                    models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Alert count"),
                ),
                (
                    "risk_level",
                    models.CharField(
                        choices=[
                            ("sem_alerta", "Sem alerta"),
                            ("atencao", "Atenção"),
                            ("alto_risco", "Alto risco"),
                        ],
                        db_index=True,
                        default="sem_alerta",
                        max_length=20,
                        verbose_name="Risk level",
                    ),
                ),
                (
                    "subscale_scores",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        verbose_name="Subscale scores",
                    ),
                ),
                (
                    "completed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Completed at"),
                ),
                (
                    "reviewed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Reviewed at"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active"),
                ),
                (
                    "municipality",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="assessments",
                        to="assessments.municipality",
                        verbose_name="Municipality",
                    ),
                ),
                (
                    "professional",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="assessments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Professional",
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assessments_reviewed",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Reviewed by",
                    ),
                ),
            ],
            options={
                "verbose_name": "Assessment evaluation",
                "verbose_name_plural": "Assessment evaluations",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="ProfessionalInvite",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=150, verbose_name="First name"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=150, verbose_name="Last name"),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, verbose_name="Email"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("expired", "Expired"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "invited_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="professional_invites",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Invited by",
                    ),
                ),
                (
                    "municipality",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invites",
                        to="assessments.municipality",
                        verbose_name="Municipality",
                    ),
                ),
            ],
            options={
                "verbose_name": "Professional invite",
                "verbose_name_plural": "Professional invites",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="ProfessionalProfile",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "registration_code",
                    models.CharField(blank=True, max_length=64, verbose_name="Registration code"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active"),
                ),
                (
                    "municipality",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="professionals",
                        to="assessments.municipality",
                        verbose_name="Municipality",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assessments_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Professional profile",
                "verbose_name_plural": "Professional profiles",
                "ordering": ["user__first_name", "user__last_name"],
            },
        ),
    ]
