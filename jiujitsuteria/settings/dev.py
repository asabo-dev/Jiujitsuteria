"""Development settings for Jiujitsuteria project."""

from .base import *
from .utils import load_env_file
import os
import dj_database_url

# ---------------------
# Load environment variables
# ---------------------
load_env_file(".env.dev", str(BASE_DIR))

# ---------------------
# Core Django Settings
# ---------------------
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ---------------------
# AWS S3 / CloudFront
# ---------------------

# Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Private bucket (videos)
AWS_PRIVATE_VIDEO_BUCKET = os.getenv("AWS_PRIVATE_VIDEO_BUCKET")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

# Public bucket (thumbnails)
AWS_PUBLIC_THUMBNAIL_BUCKET = os.getenv("AWS_PUBLIC_THUMBNAIL_BUCKET")

# CloudFront private (signed video URLs)
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN", "").replace("https://", "")
CLOUDFRONT_KEY_ID = os.getenv("CLOUDFRONT_KEY_ID")
CLOUDFRONT_KEY_FILE = os.getenv("CLOUDFRONT_KEY_FILE")
CLOUDFRONT_PRIVATE_KEY_PATH = CLOUDFRONT_KEY_FILE  # used in utils/cloudfront.py

# CloudFront public (thumbnails)
CLOUDFRONT_PUBLIC_DOMAIN = os.getenv("CLOUDFRONT_PUBLIC_DOMAIN")

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
