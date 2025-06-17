"""Upload all MP4 files from a local folder to an S3 bucket."""

import boto3
import os
from pathlib import Path

s3 = boto3.client('s3')
bucket_name = 'jiujitsuteria-videos'
local_folder = Path('/Users/quanefiom/Desktop/BJJ_app')

def upload_mp4s(local_folder):
    for local_path in local_folder.rglob('*.mp4'):
        # Generate S3 key from local path, sanitize spaces
        s3_key = str(local_path.relative_to(local_folder)).replace(' ', '_')
        print(f"Uploading {local_path} as {s3_key}...")

        s3.upload_file(
            str(local_path),
            str(bucket_name),
            str(s3_key),
            ExtraArgs={'ContentType': 'video/mp4'}
        )

upload_mp4s(local_folder)

print("✅ All MP4 files uploaded to S3.")
