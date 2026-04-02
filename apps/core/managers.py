from django.db import models


class ActiveQuerySet(models.QuerySet):
    def active(self):
        """Return only objects where `is_active=True`."""
        return self.filter(is_active=True)
