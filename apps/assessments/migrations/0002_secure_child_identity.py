import base64
import hashlib
import hmac

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from django.conf import settings
from django.db import migrations
from django.db import models

BATCH_SIZE = 500


def _normalize_child_name(value: str) -> str:
    return " ".join(str(value or "").strip().split())


def _build_child_name_cipher() -> Fernet:
    encryption_key = getattr(
        settings,
        "ASSESSMENTS_CHILD_NAME_ENCRYPTION_KEY",
        settings.SECRET_KEY,
    )
    derived_key = hashlib.sha256(encryption_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(derived_key))


def _get_blind_index_key() -> str:
    return getattr(
        settings,
        "ASSESSMENTS_CHILD_NAME_BLIND_INDEX_KEY",
        settings.SECRET_KEY,
    )


def _forward_secure_child_identity(apps, schema_editor):
    AssessmentEvaluation = apps.get_model("assessments", "AssessmentEvaluation")

    cipher = _build_child_name_cipher()
    blind_index_key = _get_blind_index_key().encode("utf-8")
    rows_to_update = []

    queryset = AssessmentEvaluation.objects.only(
        "id",
        "child_name",
        "child_name_encrypted",
        "child_name_blind_index",
    )
    for evaluation in queryset.iterator(chunk_size=BATCH_SIZE):
        normalized = _normalize_child_name(evaluation.child_name)
        if not normalized:
            if evaluation.child_name:
                evaluation.child_name = ""
                rows_to_update.append(evaluation)
        else:
            evaluation.child_name_encrypted = cipher.encrypt(
                normalized.encode("utf-8")
            ).decode("utf-8")
            evaluation.child_name_blind_index = hmac.new(
                blind_index_key,
                normalized.casefold().encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            evaluation.child_name = ""
            rows_to_update.append(evaluation)

        if len(rows_to_update) >= BATCH_SIZE:
            AssessmentEvaluation.objects.bulk_update(
                rows_to_update,
                [
                    "child_name",
                    "child_name_encrypted",
                    "child_name_blind_index",
                ],
            )
            rows_to_update.clear()

    if rows_to_update:
        AssessmentEvaluation.objects.bulk_update(
            rows_to_update,
            [
                "child_name",
                "child_name_encrypted",
                "child_name_blind_index",
            ],
        )


def _reverse_secure_child_identity(apps, schema_editor):
    AssessmentEvaluation = apps.get_model("assessments", "AssessmentEvaluation")

    cipher = _build_child_name_cipher()
    rows_to_update = []

    queryset = AssessmentEvaluation.objects.only(
        "id",
        "child_name",
        "child_name_encrypted",
        "child_name_blind_index",
    )
    for evaluation in queryset.iterator(chunk_size=BATCH_SIZE):
        encrypted_value = str(evaluation.child_name_encrypted or "").strip()
        if encrypted_value:
            try:
                evaluation.child_name = cipher.decrypt(
                    encrypted_value.encode("utf-8")
                ).decode("utf-8")
            except InvalidToken:
                evaluation.child_name = ""
        else:
            evaluation.child_name = ""

        evaluation.child_name_encrypted = ""
        evaluation.child_name_blind_index = ""
        rows_to_update.append(evaluation)

        if len(rows_to_update) >= BATCH_SIZE:
            AssessmentEvaluation.objects.bulk_update(
                rows_to_update,
                [
                    "child_name",
                    "child_name_encrypted",
                    "child_name_blind_index",
                ],
            )
            rows_to_update.clear()

    if rows_to_update:
        AssessmentEvaluation.objects.bulk_update(
            rows_to_update,
            [
                "child_name",
                "child_name_encrypted",
                "child_name_blind_index",
            ],
        )


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessmentevaluation",
            name="child_name_encrypted",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="Child name encrypted",
            ),
        ),
        migrations.AddField(
            model_name="assessmentevaluation",
            name="child_name_blind_index",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                max_length=64,
                verbose_name="Child name blind index",
            ),
        ),
        migrations.AlterField(
            model_name="assessmentevaluation",
            name="child_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                verbose_name="Child name",
            ),
        ),
        migrations.RunPython(
            _forward_secure_child_identity,
            _reverse_secure_child_identity,
        ),
    ]
