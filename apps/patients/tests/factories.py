from django.utils import timezone
from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.patients.enums import BiologicalSex
from apps.patients.enums import QuestionnaireFrequency
from apps.patients.enums import SleepDuration
from apps.patients.enums import SleepOnsetDelay
from apps.patients.models import Patient
from apps.patients.models import QuestionnaireResponse
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


class QuestionnaireResponseFactory(DjangoModelFactory):
    patient = SubFactory(PatientFactory)
    q1 = Faker("random_element", elements=SleepDuration.values)
    q2 = Faker("random_element", elements=SleepOnsetDelay.values)
    q3 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q4 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q5 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q6 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q7 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q8 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q9 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q10 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q11 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q12 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q13 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q14 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q15 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q16 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q17 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q18 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q19 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q20 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q21 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q22 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q23 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q24 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q25 = Faker("random_element", elements=QuestionnaireFrequency.values)
    q26 = Faker("random_element", elements=QuestionnaireFrequency.values)
    created = Faker("date_time_this_year", tzinfo=timezone.get_current_timezone())

    class Meta:
        model = QuestionnaireResponse
