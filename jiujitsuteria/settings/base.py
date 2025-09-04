import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# =============================================================================
# Paths & Environment
# =============================================================================
# BASE_DIR now points to the project root: /Users/quanefiom/Desktop/Github_Projects/Jiujitsuteria
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables (overridden in dev/prod if needed)
load_dotenv(BASE_DIR / ".env")

# =============================================================================
# Core Settings
# =============================================================================
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

# =============================================================================
# Applications
# =============================================================================
INSTALLED_APPS = [
    # My apps
    "bjj",
    "accounts",

    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jiujitsuteria.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # project-wide templates (optional)
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jiujitsuteria.wsgi.application"

# =============================================================================
# Database (overridden in dev/prod)
# =============================================================================
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        conn_max_age=600,
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# Static & Media Files
# =============================================================================
# URL to use when referring to static files
STATIC_URL = "/static/"

# Where Django will look for additional static files (before collectstatic)
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Project-wide static (favicon, global images/css/js)
]

# Where collectstatic will put all files (for production serving)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media (user uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# Auth Redirects
# =============================================================================
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "bjj:index"
LOGIN_URL = "/accounts/login/"

# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG" if DEBUG else "INFO",
    },
}
