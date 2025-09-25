"""Development settings for Jiujitsuteria project."""

from .base import *
from .utils import load_env_file
import os
import dj_database_url
from pathlib import Path

# ---------------------
# Load environment variables (from .env.dev if available)
# ---------------------
#load_env_file(".env.dev", str(BASE_DIR))
env_path = Path(BASE_DIR) / ".env.dev"
if env_path.exists():
    load_env_file(".env.dev", str(BASE_DIR))

# ---------------------
# Core Django Settings
# ---------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# ---------------------
# AWS S3 / CloudFront
# ---------------------
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

AWS_PRIVATE_VIDEO_BUCKET = os.getenv("AWS_PRIVATE_VIDEO_BUCKET")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

AWS_PUBLIC_THUMBNAIL_BUCKET = os.getenv("AWS_PUBLIC_THUMBNAIL_BUCKET")

CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN", "").replace("https://", "")
CLOUDFRONT_KEY_ID = os.getenv("CLOUDFRONT_KEY_ID")
CLOUDFRONT_KEY_FILE = os.getenv("CLOUDFRONT_KEY_FILE")
CLOUDFRONT_PRIVATE_KEY_PATH = CLOUDFRONT_KEY_FILE  # used in utils/cloudfront.py

CLOUDFRONT_PUBLIC_DOMAIN = os.getenv("CLOUDFRONT_PUBLIC_DOMAIN")

# ---------------------
# Database (SQLite for dev, override with DATABASE_URL if set)
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
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# ---------------------
# Security (disabled in dev)
# ---------------------
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
