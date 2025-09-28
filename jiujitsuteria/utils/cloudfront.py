import datetime
import boto3
from django.conf import settings
from botocore.signers import CloudFrontSigner
import rsa


def _rsa_signer(message):
    """Helper function for CloudFrontSigner (signs the policy with your private key)."""
    with open(settings.CLOUDFRONT_KEY_FILE, "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
    return rsa.sign(message, private_key, "SHA-1")


def generate_signed_url(key, expires_in=3600):
    """
    Generate a signed CloudFront URL for a private object.

    Args:
        key (str): Path/key in S3 (relative to the distribution).
                   e.g. "Guard/Closed_Guard/closed_guard_sweep.jpg"
        expires_in (int): Expiration time in seconds (default 1 hour).

    Returns:
        str: Signed CloudFront URL
    """
    cloudfront_domain = getattr(settings, "CLOUDFRONT_DOMAIN", None)
    key_id = getattr(settings, "CLOUDFRONT_KEY_ID", None)

    if not cloudfront_domain or not key_id:
        raise ValueError("❌ CLOUDFRONT_DOMAIN and CLOUDFRONT_KEY_ID must be set in settings.py")

    url = f"https://{cloudfront_domain}/{key}"
    expire_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    signer = CloudFrontSigner(key_id, _rsa_signer)
    signed_url = signer.generate_presigned_url(url, date_less_than=expire_date)

    return signed_url
