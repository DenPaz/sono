from django.db import models
from django.utils.translation import gettext_lazy as _


class BiologicalSex(models.TextChoices):
    MALE = "M", _("Masculino")
    FEMALE = "F", _("Feminino")


class SleepDuration(models.IntegerChoices):
    NINE_TO_ELEVEN = 1, _("9-11 horas")
    EIGHT_TO_NINE = 2, _("8-9 horas")
    SEVEN_TO_EIGHT = 3, _("7-8 horas")
    FIVE_TO_SEVEN = 4, _("5-7 horas")
    LESS_THAN_FIVE = 5, _("Menos de 5 horas")


class SleepOnsetDelay(models.IntegerChoices):
    LESS_THAN_15 = 1, _("Menos de 15 min")
    FIFTEEN_TO_30 = 2, _("15-30 min")
    THIRTY_TO_45 = 3, _("30-45 min")
    FORTY_FIVE_TO_60 = 4, _("45-60 min")
    MORE_THAN_60 = 5, _("Mais de 60 min")


class QuestionnaireFrequency(models.IntegerChoices):
    NEVER = 1, _("Nunca")
    OCCASIONALLY = 2, _("Ocasionalmente")
    SOMETIMES = 3, _("Às vezes")
    ALMOST_ALWAYS = 4, _("Quase sempre")
    ALWAYS = 5, _("Sempre")
