# jiujitsuteria/settings/dev.py
from .base import *
from .utils import load_env_file
import os
import dj_database_url

# ---------------------
# Load environment variables
# ---------------------
# BASE_DIR = Jiujitsuteria/jiujitsuteria
# BASE_DIR.parent = Jiujitsuteria/
load_env_file(".env.dev", str(BASE_DIR))

# ---------------------
# Core Django Settings
# ---------------------
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ---------------------
# Database (SQLite for dev)
# ---------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR.parent}/db.sqlite3",
        conn_max_age=0,
    )
}

# ---------------------
# Static & Media (local dev)
# ---------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # global assets (e.g. favicon, css)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# ---------------------
# Security (disabled in dev)
# ---------------------
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
