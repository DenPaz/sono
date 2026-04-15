from __future__ import annotations

from apps.assessments import constants
from apps.assessments.services.edsc_scoring import calculate_edsc_scores


def _choices_as_text(
    choices: tuple[tuple[int, str], ...],
) -> tuple[tuple[int, str], ...]:
    return tuple((value, str(label)) for value, label in choices)


def _build_answers_for_subscale_score(
    *,
    item_indexes: tuple[int, ...],
    target_score: int,
) -> dict[int, int]:
    answers = dict.fromkeys(item_indexes, 1)
    remaining_points = target_score - len(item_indexes)
    if remaining_points < 0:
        msg = "target_score cannot be lower than the minimum possible score."
        raise ValueError(msg)

    for item_index in item_indexes:
        if remaining_points <= 0:
            break
        increment = min(4, remaining_points)
        answers[item_index] += increment
        remaining_points -= increment

    if remaining_points > 0:
        msg = "target_score exceeds the maximum possible score for the subscale."
        raise ValueError(msg)

    return answers


def _answers_with_baseline(subscale_answers: dict[int, int]) -> dict[int, int]:
    answers = dict.fromkeys(range(1, constants.EDSC_ITEMS_COUNT + 1), 1)
    answers.update(subscale_answers)
    return answers


def test_edsc_questions_match_official_reference():
    official_questions = {
        1: "Quantas horas a criança dorme durante a noite?",
        2: "Quanto tempo a criança demora para adormecer?",
        3: "A criança não quer ir para a cama para dormir",
        4: "A criança tem dificuldade para adormecer",
        5: "Antes de adormecer a criança está agitada, nervosa ou sente medo",
        6: 'A criança apresenta "movimentos bruscos", repuxões ou tremores ao adormecer',
        7: "Durante a noite a criança faz movimentos rítmicos com a cabeça e corpo",
        8: 'A criança diz que está vendo "coisas estranhas" um pouco antes de adormecer',
        9: "A criança transpira muito ao adormecer",
        10: "A criança acorda mais de duas vezes durante a noite",
        11: "A criança acorda durante a noite e tem dificuldade em adormecer novamente",
        12: "A criança mexe-se continuamente durante o sono",
        13: "A criança não respira bem durante o sono",
        14: "A criança para de respirar por alguns instantes durante o sono",
        15: "A criança ronca",
        16: "A criança transpira muito durante a noite",
        17: "A criança levanta-se e senta-se na cama ou anda enquanto dorme",
        18: "A criança fala durante o sono",
        19: "A criança range os dentes durante o sono",
        20: "Durante o sono a criança grita angustiada, sem conseguir acordar",
        21: "A criança tem pesadelos que não lembra no dia seguinte",
        22: "A criança tem dificuldade em acordar pela manhã",
        23: "Acorda cansada pela manhã",
        24: (
            "Ao acordar a criança não consegue movimentar-se "
            "ou fica como se estivesse paralisada por uns minutos"
        ),
        25: "A criança sente-se sonolenta durante o dia",
        26: "Durante o dia a criança adormece em situações inesperadas sem avisar",
    }

    assert constants.EDSC_ITEMS_COUNT == 26
    assert tuple(constants.EDSC_QUESTIONS.keys()) == tuple(range(1, 27))
    assert {
        item_index: str(question)
        for item_index, question in constants.EDSC_QUESTIONS.items()
    } == official_questions


def test_edsc_item_1_and_2_choices_match_official_reference():
    assert _choices_as_text(constants.EDSC_ITEM_1_SCALE_CHOICES) == (
        (1, "9-11 horas"),
        (2, "8-9 horas"),
        (3, "7-8 horas"),
        (4, "5-7 horas"),
        (5, "Menos de 5 horas"),
    )

    assert _choices_as_text(constants.EDSC_ITEM_2_SCALE_CHOICES) == (
        (1, "Menos de 15 min"),
        (2, "15-30 min"),
        (3, "30-45 min"),
        (4, "45-60 min"),
        (5, "Mais de 60 min"),
    )


def test_standard_frequency_scale_applies_to_items_3_to_26():
    expected_standard_choices = _choices_as_text(constants.EDSC_STANDARD_SCALE_CHOICES)
    assert _choices_as_text(
        constants.get_item_scale_choices(item_index=1)
    ) == _choices_as_text(constants.EDSC_ITEM_1_SCALE_CHOICES)
    assert _choices_as_text(
        constants.get_item_scale_choices(item_index=2)
    ) == _choices_as_text(constants.EDSC_ITEM_2_SCALE_CHOICES)

    for item_index in range(3, 27):
        assert (
            _choices_as_text(constants.get_item_scale_choices(item_index=item_index))
            == expected_standard_choices
        )


def test_subscale_groups_and_limits_match_official_reference():
    expected_subscales = {
        "disturbios_inicio_manutencao_sono": {
            "item_indexes": (1, 2, 3, 4, 5, 10, 11),
            "acceptable_max": 21,
        },
        "disturbios_respiratorios_sono": {
            "item_indexes": (13, 14, 15),
            "acceptable_max": 6,
        },
        "disturbios_despertar": {
            "item_indexes": (17, 20, 21),
            "acceptable_max": 11,
        },
        "disturbios_transicao_sono_vigilia": {
            "item_indexes": (6, 7, 8, 12, 18, 19),
            "acceptable_max": 23,
        },
        "sonolencia_excessiva_diurna": {
            "item_indexes": (22, 23, 24, 25, 26),
            "acceptable_max": 19,
        },
        "hiperhidrose_sono": {
            "item_indexes": (9, 16),
            "acceptable_max": 7,
        },
    }

    current_subscales = {
        key: {
            "item_indexes": definition["item_indexes"],
            "acceptable_max": definition["acceptable_max"],
        }
        for key, definition in constants.EDSC_SUBSCALE_DEFINITIONS.items()
    }

    assert current_subscales == expected_subscales

    covered_items = sorted(
        item_index
        for definition in constants.EDSC_SUBSCALE_DEFINITIONS.values()
        for item_index in definition["item_indexes"]
    )
    assert covered_items == list(range(1, 27))


def test_subscale_alert_logic_uses_strictly_greater_than_acceptable_max():
    for key, definition in constants.EDSC_SUBSCALE_DEFINITIONS.items():
        item_indexes = definition["item_indexes"]
        acceptable_max = definition["acceptable_max"]

        answers_at_limit = _answers_with_baseline(
            _build_answers_for_subscale_score(
                item_indexes=item_indexes,
                target_score=acceptable_max,
            )
        )
        result_at_limit = calculate_edsc_scores(answers=answers_at_limit)
        assert result_at_limit.subscales[key].score == acceptable_max
        assert result_at_limit.subscales[key].is_alert is False

        answers_above_limit = dict(answers_at_limit)
        editable_item_index = next(
            index
            for index in item_indexes
            if answers_above_limit[index] < constants.EDSC_MAX_ITEM_VALUE
        )
        answers_above_limit[editable_item_index] += 1

        result_above_limit = calculate_edsc_scores(answers=answers_above_limit)
        assert result_above_limit.subscales[key].score == acceptable_max + 1
        assert result_above_limit.subscales[key].is_alert is True


def test_total_score_is_sum_of_all_partial_scores():
    answers = {
        item_index: ((item_index - 1) % constants.EDSC_MAX_ITEM_VALUE) + 1
        for item_index in range(1, constants.EDSC_ITEMS_COUNT + 1)
    }

    result = calculate_edsc_scores(answers=answers)
    expected_total = sum(subscale.score for subscale in result.subscales.values())

    assert result.total_score == expected_total
