from .base import *
from .utils import load_env_file
import os
import dj_database_url

# ---------------------
# Load environment variables
# ---------------------
load_env_file(".env.prod", str(BASE_DIR.parent))

# ---------------------
# Core Django Settings
# ---------------------
DEBUG = False
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# ---------------------
# Database
# ---------------------
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ---------------------
# Static Files
# ---------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Add your app’s static folder so collectstatic finds styles/js
STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, "bjj", "static"),
]

# ---------------------
# Media Files (S3/CloudFront)
# ---------------------
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "ap-southeast-1")

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

if CLOUDFRONT_DOMAIN:
    MEDIA_URL = f"https://{CLOUDFRONT_DOMAIN}/"
else:
    MEDIA_URL = (
        f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"
    )

# ---------------------
# Security
# ---------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

⚠️ Enable only after HTTPS / Route53 + SSL certs are set up
SECURE_SSL_REDIRECT = True

