from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.templatetags.static import static


def get_user_upload_path(instance, filename) -> str:
    return f"users/user_{instance.user.id}/{filename}"


def get_default_avatar_url() -> str:
    return static("images/default-avatar.png")


def send_invitation_email(request, user) -> None:
    with transaction.atomic():
        EmailAddress.objects.update_or_create(
            user=user,
            email=user.email,
            defaults={"verified": True, "primary": True},
        )
    current_site = get_current_site(request)
    context = {
        "user": user,
        "uid": user_pk_to_url_str(user),
        "token": default_token_generator.make_token(user),
        "site_name": current_site.name,
        "domain": current_site.domain,
        "protocol": "https" if request.is_secure() else "http",
    }
    get_adapter().send_mail("users/email/invitation", user.email, context)
