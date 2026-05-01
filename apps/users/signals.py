from django.apps import apps
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save
from django.dispatch import receiver

from .enums import UserRole
from .models import Admin
from .models import AdminProfile
from .models import Parent
from .models import ParentProfile
from .models import Specialist
from .models import SpecialistProfile
from .models import User


@receiver(post_migrate, sender=apps.get_app_config("users"))
def create_user_groups(sender, **kwargs):
    with transaction.atomic():
        for group_name in UserRole.values:
            Group.objects.get_or_create(name=group_name)


@receiver(post_save, sender=User)
@receiver(post_save, sender=Admin)
@receiver(post_save, sender=Specialist)
@receiver(post_save, sender=Parent)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if not instance.role:
        return

    profile_model = {
        UserRole.ADMIN: AdminProfile,
        UserRole.SPECIALIST: SpecialistProfile,
        UserRole.PARENT: ParentProfile,
    }.get(instance.role)

    with transaction.atomic():
        if profile_model is not None:
            profile_model.objects.get_or_create(user=instance)

        group = Group.objects.get(name=instance.role)
        instance.groups.add(group)
