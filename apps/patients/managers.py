from django.db import models

from apps.core.managers import ActiveQuerySet


class PatientQuerySet(ActiveQuerySet):
    def with_relations(self):
        return self.select_related("parent", "specialist")


class PatientManager(models.Manager.from_queryset(PatientQuerySet)):
    pass
