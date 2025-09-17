"""
Wrapper for CloudFront signed URL generation in production.

This ensures that object keys are normalized (no leading slash),
so CloudFront signed URLs won’t break with AccessDenied errors.
"""

from jiujitsuteria.utils.cloudfront import generate_signed_url as _generate_signed_url


def generate_signed_url(object_key: str, *args, **kwargs) -> str:
    # Strip any leading slash from the key
    normalized_key = object_key.lstrip("/")
    return _generate_signed_url(normalized_key, *args, **kwargs)
