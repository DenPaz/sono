from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from apps.assessments import constants

RiskLevel = Literal["sem_alerta", "atencao", "alto_risco"]


@dataclass(frozen=True, slots=True)
class EdscSubscaleResult:
    key: str
    label: str
    item_indexes: tuple[int, ...]
    score: int
    acceptable_max: int
    is_alert: bool


@dataclass(frozen=True, slots=True)
class EdscScoreResult:
    total_score: int
    min_total: int
    max_total: int
    alert_count: int
    risk_level: RiskLevel
    subscales: dict[str, EdscSubscaleResult]


def normalize_edsc_answers(
    raw_answers: Mapping[int | str, int | str],
) -> dict[int, int]:
    normalized: dict[int, int] = {}
    for raw_item_index, raw_value in raw_answers.items():
        try:
            item_index = int(raw_item_index)
            score = int(raw_value)
        except (TypeError, ValueError) as exc:
            msg = (
                "All EDSC answers must be integer-compatible values. "
                f"Invalid pair: ({raw_item_index!r}, {raw_value!r})."
            )
            raise ValueError(msg) from exc
        normalized[item_index] = score
    return normalized


def validate_edsc_answers(answers: Mapping[int, int]) -> None:
    expected_indexes = set(range(1, constants.EDSC_ITEMS_COUNT + 1))
    received_indexes = set(answers.keys())

    missing_indexes = sorted(expected_indexes - received_indexes)
    extra_indexes = sorted(received_indexes - expected_indexes)
    if missing_indexes or extra_indexes:
        msg = (
            "EDSC answers must contain exactly 26 answers (indexes 1..26). "
            f"Missing: {missing_indexes}; Extra: {extra_indexes}."
        )
        raise ValueError(msg)

    for item_index, score in answers.items():
        if (
            score < constants.EDSC_MIN_ITEM_VALUE
            or score > constants.EDSC_MAX_ITEM_VALUE
        ):
            msg = (
                f"Invalid score for item {item_index}: {score}. "
                f"Expected values between {constants.EDSC_MIN_ITEM_VALUE} and "
                f"{constants.EDSC_MAX_ITEM_VALUE}."
            )
            raise ValueError(msg)


def calculate_subscale_score(
    *, answers: Mapping[int, int], item_indexes: tuple[int, ...]
) -> int:
    return sum(answers[item_index] for item_index in item_indexes)


def calculate_edsc_subscales(
    answers: Mapping[int, int],
) -> dict[str, EdscSubscaleResult]:
    validate_edsc_answers(answers=answers)

    subscales: dict[str, EdscSubscaleResult] = {}
    for key, definition in constants.EDSC_SUBSCALE_DEFINITIONS.items():
        item_indexes = definition["item_indexes"]
        acceptable_max = definition["acceptable_max"]
        score = calculate_subscale_score(
            answers=answers,
            item_indexes=item_indexes,
        )
        subscales[key] = EdscSubscaleResult(
            key=key,
            label=str(definition["label"]),
            item_indexes=item_indexes,
            score=score,
            acceptable_max=acceptable_max,
            is_alert=score > acceptable_max,
        )
    return subscales


def calculate_alert_count(subscales: Mapping[str, EdscSubscaleResult]) -> int:
    return sum(int(subscale.is_alert) for subscale in subscales.values())


def classify_risk_level(alert_count: int) -> RiskLevel:
    if alert_count <= 0:
        return constants.RISK_LEVEL_NO_ALERT
    if alert_count <= 2:
        return constants.RISK_LEVEL_ATTENTION
    return constants.RISK_LEVEL_HIGH


def calculate_edsc_scores(answers: Mapping[int, int]) -> EdscScoreResult:
    normalized_answers = normalize_edsc_answers(raw_answers=answers)
    validate_edsc_answers(answers=normalized_answers)

    subscales = calculate_edsc_subscales(answers=normalized_answers)
    total_score = sum(subscale.score for subscale in subscales.values())
    alert_count = calculate_alert_count(subscales=subscales)

    return EdscScoreResult(
        total_score=total_score,
        min_total=constants.EDSC_MIN_TOTAL_SCORE,
        max_total=constants.EDSC_MAX_TOTAL_SCORE,
        alert_count=alert_count,
        risk_level=classify_risk_level(alert_count=alert_count),
        subscales=subscales,
    )
