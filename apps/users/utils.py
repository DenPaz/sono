from django.templatetags.static import static


def get_user_upload_path(instance, filename) -> str:
    """Return the path to upload user-related files."""
    return f"users/{instance.user.id}/{filename}"


def get_default_avatar_url() -> str:
    """Return the URL of the default avatar image."""
    return static("images/default-avatar.png")
