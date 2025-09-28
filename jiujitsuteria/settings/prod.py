"""Production settings for Jiujitsuteria project."""

from .base import *
from .utils import load_env_file
import os
import sys
import dj_database_url

# =============================================================================
# Environment
# =============================================================================
# On EC2, load environment variables from the shared folder
shared_env_path = BASE_DIR / "shared" / ".env.prod"
if not shared_env_path.exists():
    sys.exit(f"❌ Required environment file not found: {shared_env_path}")

load_env_file(".env.prod", str(BASE_DIR / "shared"))

DEBUG = False

# Allowed hosts (set in .env.prod)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "jiujitsuteria.com,www.jiujitsuteria.com").split(",")

# =============================================================================
# AWS S3 / CloudFront
# =============================================================================
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

# Private bucket (videos)
AWS_PRIVATE_VIDEO_BUCKET = os.getenv("AWS_PRIVATE_VIDEO_BUCKET")

# Public bucket (thumbnails)
AWS_PUBLIC_THUMBNAIL_BUCKET = os.getenv("AWS_PUBLIC_THUMBNAIL_BUCKET")

# CloudFront private (signed video URLs)
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN", "").replace("https://", "")
CLOUDFRONT_KEY_ID = os.getenv("CLOUDFRONT_KEY_ID")
CLOUDFRONT_PRIVATE_KEY_PATH = os.getenv("CLOUDFRONT_PRIVATE_KEY_PATH")
# Alias for backward compatibility with cloudfront.py
CLOUDFRONT_KEY_FILE = CLOUDFRONT_PRIVATE_KEY_PATH

# CloudFront public (unsigned thumbnail URLs)
CLOUDFRONT_PUBLIC_DOMAIN = os.getenv("CLOUDFRONT_PUBLIC_DOMAIN", "").replace("https://", "")

# =============================================================================
# Database (PostgreSQL on RDS)
# =============================================================================
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# =============================================================================
# Static & Media (Production)
# =============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =============================================================================
# Security
# =============================================================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
