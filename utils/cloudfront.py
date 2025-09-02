"""This module provides a utility function to generate signed URLs for AWS CloudFront
using a custom policy. It uses the RSA algorithm to sign the policy and returns a URL
with the necessary parameters for accessing protected resources."""

import base64
import rsa
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone


def generate_signed_url(resource_url, key_id, private_key_path, expire_minutes=30):
    """
    Generate a signed CloudFront URL using a custom policy.

    Args:
        resource_url (str): Full CloudFront resource URL (e.g., https://d1234.cloudfront.net/videos/myvideo.mp4)
        key_id (str): CloudFront key pair ID
        private_key_path (str): Path to your downloaded private key (.pem) file
        expire_minutes (int): How long the URL should stay valid (default: 30 minutes)

    Returns:
        str: Signed URL with CloudFront signature parameters
    """

    # Set expiry time in UTC epoch format
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    epoch_time = int(expire_time.timestamp())

    # Define the custom policy JSON
    policy = f'''{{
        "Statement": [
            {{
                "Resource": "{resource_url}",
                "Condition": {{
                    "DateLessThan": {{
                        "AWS:EpochTime": {epoch_time}
                    }}
                }}
            }}
        ]
    }}'''

    # Load the private key (.pem) file
    with open(private_key_path, 'rb') as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())

    # Sign the policy using SHA1
    signature = rsa.sign(policy.encode('utf-8'), private_key, 'SHA-1')

    # Base64 encode and replace CloudFront-restricted characters
    encoded_signature = base64.b64encode(signature).decode('utf-8')
    encoded_signature = encoded_signature.replace('+', '-').replace('=', '_').replace('/', '~')

    # Base64 encode the policy itself
    encoded_policy = base64.b64encode(policy.encode('utf-8')).decode('utf-8')

    # Build the final query string
    params = {
        'Policy': encoded_policy,
        'Signature': encoded_signature,
        'Key-Pair-Id': key_id
    }

    # Return the signed URL
    return f"{resource_url}?{urlencode(params)}"
