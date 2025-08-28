from .base import *
from .utils import load_env_file
import os

# Load environment variables from .env.dev
load_env_file(".env.dev", str(BASE_DIR.parent))

DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:////Users/quanefiom/Desktop/Github_Projects/Jiujitsuteria/db.sqlite3"
    )
}


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Security (disabled for dev)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
