"""Development settings: use local SQLite, static files, and media storage."""

from .base import *
from .utils import load_env_file
import os
import dj_database_url
from pathlib import Path


# ---------------------
# Load environment variables
# ---------------------
env_path = Path(BASE_DIR) / ".env.dev"

if env_path.exists():
    load_env_file(".env.dev", str(BASE_DIR))


# ---------------------
# Core Django Settings
# ---------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-dev-key")

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost"
).split(",")


# ---------------------
# Database (SQLite for development)
# ---------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR.parent}/db.sqlite3",
        conn_max_age=0,
    )
}


# ---------------------
# Static & Media (local development)
# ---------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ---------------------
# Local BJJ video storage
# ---------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = Path("/Users/quanefiom/desktop/BJJ/bjj_videos")


# ---------------------
# Security (disabled in development)
# ---------------------
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False