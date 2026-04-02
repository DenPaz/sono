from factory import Faker
from factory import LazyAttributeSequence
from factory import RelatedFactory
from factory import Trait
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.django import ImageField

from apps.users.models import User
from apps.users.models import UserProfile


class UserFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttributeSequence(
        lambda o, n: (
            f"{o.first_name.lower()}_{o.last_name.lower()}_{n + 1}@example.com"
        ),
    )
    is_active = True
    is_staff = False
    is_superuser = False

    profile = RelatedFactory(
        "apps.users.tests.factories.UserProfileFactory",
        factory_related_name="user",
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
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        ).evaluate(None, None, extra={"locale": None})
        self.set_password(password)
        self.save(update_fields=["password"])


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    class Params:
        with_avatar = Trait(avatar=ImageField(filename="avatar.jpg"))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.pop("user")
        profile, _ = model_class.objects.update_or_create(
            user=user,
            defaults=kwargs,
        )
        return profile
