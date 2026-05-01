from django.templatetags.static import static


def get_user_upload_path(instance, filename) -> str:
    return f"users/user_{instance.user.id}/{filename}"


def get_default_avatar_url() -> str:
    return static("images/default-avatar.png")
