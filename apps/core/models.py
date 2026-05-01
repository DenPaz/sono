from model_utils.models import TimeStampedModel
from model_utils.models import UUIDModel


class BaseModel(TimeStampedModel, UUIDModel):
    """
    Base model for all models in the application. It provides a UUID primary
    key and timestamp fields for created and modified times.
    """

    class Meta:
        abstract = True
