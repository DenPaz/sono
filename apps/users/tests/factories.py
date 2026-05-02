from factory import Faker
from factory import LazyAttributeSequence
from factory import LazyFunction
from factory import SubFactory
from factory import Trait
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.django import ImageField
from faker import Faker as FakerLib

from apps.users.models import Admin
from apps.users.models import AdminProfile
from apps.users.models import Parent
from apps.users.models import ParentProfile
from apps.users.models import Specialist
from apps.users.models import SpecialistProfile
from apps.users.models import User

faker_pt_br = FakerLib("pt_BR")


class UserFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttributeSequence(
        lambda o, n: f"{o.first_name.lower()}_{o.last_name.lower()}_{n + 1}@example.com"
    )

    class Meta:
        model = User
        skip_postgeneration_save = True

    @post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or Faker(
            "password",
            length=42,
            digits=True,
            upper_case=True,
            lower_case=True,
            special_chars=True,
        ).evaluate(None, None, extra={"locale": None})
        self.set_password(password)
        self.save(update_fields=["password"])


class AdminFactory(UserFactory):
    class Meta:
        model = Admin
        skip_postgeneration_save = True


class SpecialistFactory(UserFactory):
    class Meta:
        model = Specialist
        skip_postgeneration_save = True


class ParentFactory(UserFactory):
    class Meta:
        model = Parent
        skip_postgeneration_save = True


class AdminProfileFactory(DjangoModelFactory):
    user = SubFactory(AdminFactory)

    class Meta:
        model = AdminProfile
        django_get_or_create = ("user",)

    class Params:
        with_avatar = Trait(avatar=ImageField(filename="avatar.jpg"))


class SpecialistProfileFactory(DjangoModelFactory):
    user = SubFactory(SpecialistFactory)

    class Meta:
        model = SpecialistProfile
        django_get_or_create = ("user",)

    class Params:
        with_avatar = Trait(avatar=ImageField(filename="avatar.jpg"))


class ParentProfileFactory(DjangoModelFactory):
    user = SubFactory(ParentFactory)
    phone = LazyFunction(faker_pt_br.cellphone_number)
    birth_date = Faker("date_of_birth", minimum_age=18, maximum_age=60)
    address = LazyFunction(
        lambda: {
            "postal_code": faker_pt_br.postcode(),
            "street": faker_pt_br.street_name(),
            "number": faker_pt_br.building_number(),
            "complement": "",
            "neighborhood": faker_pt_br.bairro(),
            "city": faker_pt_br.city(),
            "state": faker_pt_br.estado_sigla(),
        }
    )

    class Meta:
        model = ParentProfile
        django_get_or_create = ("user",)

    class Params:
        with_avatar = Trait(avatar=ImageField(filename="avatar.jpg"))
