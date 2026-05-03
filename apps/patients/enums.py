from django.db import models
from django.utils.translation import gettext_lazy as _


class BiologicalSex(models.TextChoices):
    MALE = "M", _("Male")
    FEMALE = "F", _("Female")


class SleepDuration(models.IntegerChoices):
    NINE_TO_ELEVEN = 1, _("9-11 hours")
    EIGHT_TO_NINE = 2, _("8-9 hours")
    SEVEN_TO_EIGHT = 3, _("7-8 hours")
    FIVE_TO_SEVEN = 4, _("5-7 hours")
    LESS_THAN_FIVE = 5, _("Less than 5 hours")


class SleepOnsetDelay(models.IntegerChoices):
    LESS_THAN_15 = 1, _("Less than 15 min")
    FIFTEEN_TO_30 = 2, _("15-30 min")
    THIRTY_TO_45 = 3, _("30-45 min")
    FORTY_FIVE_TO_60 = 4, _("45-60 min")
    MORE_THAN_60 = 5, _("More than 60 min")


class QuestionnaireFrequency(models.IntegerChoices):
    NEVER = 1, _("Never")
    OCCASIONALLY = 2, _("Occasionally")
    SOMETIMES = 3, _("Sometimes")
    ALMOST_ALWAYS = 4, _("Almost always")
    ALWAYS = 5, _("Always")
