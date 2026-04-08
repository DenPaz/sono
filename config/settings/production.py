# ruff: noqa: E501
"""Django settings for production."""

from .base import *  # noqa: F403
from .base import DATABASES
from .base import INSTALLED_APPS
from .base import REDIS_URL
from .base import env

# -----------------------------------------------------------------------------
# GENERAL
# -----------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["sono-app.com.br"],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=["https://sono-app.com.br"],
)

# -----------------------------------------------------------------------------
# DATABASES
# -----------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# -----------------------------------------------------------------------------
# CACHES
# -----------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# -----------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "__Secure-sessionid"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_NAME = "__Secure-csrftoken"
SECURE_HSTS_SECONDS = 518400
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", True)

# -----------------------------------------------------------------------------
# STORAGES
# -----------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
AWS_QUERYSTRING_AUTH = False
_AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}
AWS_S3_MAX_MEMORY_SIZE = env.int("DJANGO_AWS_S3_MAX_MEMORY_SIZE", default=100_000_000)
AWS_S3_REGION_NAME = env("DJANGO_AWS_S3_REGION_NAME", default=None)
AWS_S3_CUSTOM_DOMAIN = env("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)
aws_s3_domain = AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# -----------------------------------------------------------------------------
# STATIC & MEDIA
# -----------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = f"https://{aws_s3_domain}/media/"

# -----------------------------------------------------------------------------
# EMAIL
# -----------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="Sono <noreply@sono-app.com.br>",
)
SERVER_EMAIL = env(
    "DJANGO_SERVER_EMAIL",
    default=DEFAULT_FROM_EMAIL,
)
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[Sono] ",
)
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX

# -----------------------------------------------------------------------------
# ADMIN
# -----------------------------------------------------------------------------
ADMIN_URL = env("DJANGO_ADMIN_URL")

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

# -----------------------------------------------------------------------------
# anymail
# -----------------------------------------------------------------------------
INSTALLED_APPS += ["anymail"]
EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
AWS_SES_REGION_NAME = env("DJANGO_AWS_SES_REGION_NAME", default="sa-east-1")
ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_SES_REGION_NAME,
        "config": {
            "connect_timeout": 30,
            "read_timeout": 30,
        },
    },
}
