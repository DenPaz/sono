"""Django settings for tests."""

from .base import *  # noqa: F403
from .base import TEMPLATES
from .base import env

# -----------------------------------------------------------------------------
# GENERAL
# -----------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="1ns3cure-s3cr3t-k3y-f0r-t3st1ng")
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# -----------------------------------------------------------------------------
# PASSWORDS
# -----------------------------------------------------------------------------
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# -----------------------------------------------------------------------------
# EMAIL
# -----------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# -----------------------------------------------------------------------------
# DEBUGGING FOR TEMPLATES
# -----------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True

# -----------------------------------------------------------------------------
# MEDIA
# -----------------------------------------------------------------------------
MEDIA_URL = "http://media.testserver/"
