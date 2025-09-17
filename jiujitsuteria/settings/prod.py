"""Production settings for Jiujitsuteria project."""

from .base import *
from .utils import load_env_file
import os
import dj_database_url

# =============================================================================
# Environment
# =============================================================================
# Load environment variables from .env.prod
load_env_file(".env.prod", str(BASE_DIR))

DEBUG = False

# Allowed hosts (set in .env.prod)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

# =============================================================================
# AWS S3 / CloudFront
# =============================================================================
# Credentials
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
# Collected static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise for static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media (thumbnails only, served via CloudFront)
MEDIA_URL = f"https://{CLOUDFRONT_PUBLIC_DOMAIN}/"
MEDIA_ROOT = BASE_DIR / "media"  # optional, used only if you store files locally

# Note: Do NOT set DEFAULT_FILE_STORAGE for private videos; generate signed URLs in views

# =============================================================================
# Security
# =============================================================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
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

# =============================================================================
# Notes for developers
# =============================================================================
# - Thumbnails: public S3 + CloudFront, use MEDIA_URL in templates
# - Videos: private S3 + signed CloudFront URLs, generate signed URLs in views
# - Example usage for videos:
#   from bjj.utils import generate_signed_url
#   video_url = generate_signed_url(s3_key, CLOUDFRONT_DOMAIN, CLOUDFRONT_KEY_ID, CLOUDFRONT_PRIVATE_KEY_PATH)

