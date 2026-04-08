from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel


class BaseModel(UUIDModel, TimeStampedModel):
    class Meta:
        abstract = True
