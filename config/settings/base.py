# ruff: noqa: E501
"""Base Django settings."""

import ssl
from pathlib import Path

import environ
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _

# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# -----------------------------------------------------------------------------
# ENVIRONMENT
# -----------------------------------------------------------------------------
env = environ.Env()
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", False)
if READ_DOT_ENV_FILE:
    env.read_env(str(BASE_DIR / ".env"))

# -----------------------------------------------------------------------------
# GENERAL
# -----------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", False)
TIME_ZONE = "America/Sao_Paulo"
LANGUAGE_CODE = "pt-br"
LANGUAGES = [
    ("en", _("English")),
    ("pt-br", _("Portuguese")),
]
SITE_ID = 1
SITE_NAME = "Sono"
SITE_DOMAIN = "sono-app.com.br"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# -----------------------------------------------------------------------------
# DATABASES
# -----------------------------------------------------------------------------
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="sqlite:///db.sqlite3",
    ),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# URLS
# -----------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# -----------------------------------------------------------------------------
# APPS
# -----------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_tailwind",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "django_celery_beat",
    "django_vite",
    "django_filters",
    "django_jsonform",
    "phonenumber_field",
    "formtools",
    "braces",
    "extra_views",
    "django_htmx",
    "widget_tweaks",
    "django_cotton",
]
LOCAL_APPS = [
    "apps.core.config.CoreConfig",
    "apps.dashboard.config.DashboardConfig",
    "apps.users.config.UsersConfig",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# -----------------------------------------------------------------------------
# MIGRATIONS
# -----------------------------------------------------------------------------
MIGRATION_MODULES = {}

# -----------------------------------------------------------------------------
# AUTHENTICATION
# -----------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "account_login"
LOGIN_URL = "account_login"

# -----------------------------------------------------------------------------
# PASSWORDS
# -----------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "apps.users.password_validation.UppercaseValidator"},
    {"NAME": "apps.users.password_validation.LowercaseValidator"},
    {"NAME": "apps.users.password_validation.SymbolValidator"},
]

# -----------------------------------------------------------------------------
# MIDDLEWARE
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "apps.core.middleware.HtmxMessagesMiddleware",
]

# -----------------------------------------------------------------------------
# STATIC
# -----------------------------------------------------------------------------
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# -----------------------------------------------------------------------------
# MEDIA
# -----------------------------------------------------------------------------
MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"

# -----------------------------------------------------------------------------
# TEMPLATES
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "apps.users.context_processors.allauth_settings",
            ],
        },
    },
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
CRISPY_TEMPLATE_PACK = "tailwind"
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------
FIXTURE_DIRS = (str(BASE_DIR / "fixtures"),)

# -----------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# -----------------------------------------------------------------------------
# EMAIL
# -----------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_TIMEOUT = 5

# -----------------------------------------------------------------------------
# ADMIN
# -----------------------------------------------------------------------------
ADMIN_URL = "admin/"
ADMINS = [
    ("""Dennis Paz""", "dppazlopez@gmail.com"),
    ("""Alisson Pereira""", "alissonpef@gmail.com"),
]
MANAGERS = ADMINS
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", True)

# -----------------------------------------------------------------------------
# MESSAGES
# -----------------------------------------------------------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "info",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}

# -----------------------------------------------------------------------------
# redis
# -----------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
REDIS_SSL = REDIS_URL.startswith("rediss://")

# -----------------------------------------------------------------------------
# celery
# -----------------------------------------------------------------------------
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = REDIS_URL
CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE} if REDIS_SSL else None
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# -----------------------------------------------------------------------------
# django-allauth
# -----------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = [
    "first_name*",
    "last_name*",
    "email*",
    "password1*",
    "password2*",
]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_ADAPTER = "apps.users.adapters.AccountAdapter"
ACCOUNT_FORMS = {
    "signup": "apps.users.forms_allauth.UserSignupForm",
}
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_CHANGE_EMAIL = True

# -----------------------------------------------------------------------------
# django-vite
# -----------------------------------------------------------------------------
DJANGO_VITE = {
    "default": {
        "dev_mode": env.bool("DJANGO_VITE_DEV_MODE", default=False),
        "dev_server_host": env("DJANGO_VITE_SERVER_HOST", default="localhost"),
        "dev_server_port": env.int("DJANGO_VITE_SERVER_PORT", default=5173),
        "manifest_path": str(BASE_DIR / "static" / "dist" / ".vite" / "manifest.json"),
    },
}

# -----------------------------------------------------------------------------
# django-cotton
# -----------------------------------------------------------------------------
COTTON_DIR = "components"

# -----------------------------------------------------------------------------
# django-phonenumber-field
# -----------------------------------------------------------------------------
PHONENUMBER_DEFAULT_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_REGION = "BR"
