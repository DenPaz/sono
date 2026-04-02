from django.templatetags.static import static


def get_default_image_url() -> str:
    """Return the URL of the default image."""
    return static("images/default-image.png")
