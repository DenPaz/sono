from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.patients.enums import BiologicalSex
from apps.patients.models import Patient
from apps.users.tests.factories import ParentFactory
from apps.users.tests.factories import SpecialistFactory


class PatientFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    birth_date = Faker("date_of_birth", minimum_age=1, maximum_age=17)
    biological_sex = Faker("random_element", elements=BiologicalSex.values)
    notes = Faker("paragraph", nb_sentences=10)
    parent = SubFactory(ParentFactory)
    specialist = SubFactory(SpecialistFactory)
    is_active = True

    class Meta:
        model = Patient
