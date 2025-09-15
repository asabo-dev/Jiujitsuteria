"""
Utilities for generating signed CloudFront URLs for secure access to private video objects.
"""

import os
from datetime import datetime, timedelta, timezone
from django.conf import settings
from botocore.signers import CloudFrontSigner
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def _rsa_signer(message: bytes) -> bytes:
    """Helper for CloudFrontSigner: signs the policy with your private key."""
    key_file_path = getattr(settings, "CLOUDFRONT_KEY_FILE", None)

    if not key_file_path or not os.path.exists(key_file_path):
        raise FileNotFoundError(f"❌ CloudFront private key file not found: {key_file_path}")

    try:
        with open(key_file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # CloudFront keys typically don't use passwords
            )

        return private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA1()  # CloudFront requires RSA-SHA1
        )

    except Exception as e:
        raise ValueError(f"❌ Failed to load/sign with private key: {str(e)}")


def generate_signed_video_url(key: str, expires_in: int = 3600) -> str:
    """
    Generate a signed CloudFront URL for a private video.

    Args:
        key (str): Path/key in S3 (relative to the distribution).
                   e.g. "videos/guard/closed_guard.mp4"
        expires_in (int): Expiration time in seconds (default 1 hour).

    Returns:
        str: Signed CloudFront URL
    """
    cloudfront_domain = getattr(settings, "CLOUDFRONT_DOMAIN", None)
    key_id = getattr(settings, "CLOUDFRONT_KEY_ID", None)  # CloudFront Key Pair ID (Kxxxxxxx)
    key_file_path = getattr(settings, "CLOUDFRONT_KEY_FILE", None)

    if not cloudfront_domain:
        raise ValueError("❌ CLOUDFRONT_DOMAIN must be set in settings.py")
    if not key_id:
        raise ValueError("❌ CLOUDFRONT_KEY_ID must be set in settings.py (use CloudFront Key Pair ID starting with 'K')")
    if not key_file_path:
        raise ValueError("❌ CLOUDFRONT_KEY_FILE must be set in settings.py")

    # Normalize key (remove leading slashes)
    key = key.lstrip('/')

    # Full URL before signing
    url = f"https://{cloudfront_domain}/{key}"

    # Expiration time
    expire_date = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    try:
        signer = CloudFrontSigner(key_id, _rsa_signer)
        return signer.generate_presigned_url(url, date_less_than=expire_date)
    except Exception as e:
        raise ValueError(f"❌ Failed to generate signed URL: {str(e)}")


def test_signed_video_url():
    """Quick test function to validate your CloudFront setup."""
    try:
        test_key = "test-video.mp4"
        signed_url = generate_signed_video_url(test_key, expires_in=300)  # 5 minutes
        print(f"✅ Successfully generated signed video URL: {signed_url}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
