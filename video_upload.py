"""
This script uploads videos from a local folder to an AWS S3 bucket,
sanitizes filenames, and saves clean CloudFront URLs into the Django DB.

⚡️ Key improvements:
1. Saves only the clean CloudFront URL (no ?v=timestamp).
2. Relies on Video.updated_at in templates for cache busting.
3. Updates existing Video entries instead of duplicating.
"""

import os
import re
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import django

# --- Path setup ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Setup Django Environment ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jiujitsuteria.settings")
django.setup()

from bjj.models import Video  # ✅ ensure Video model has `updated_at = models.DateTimeField(auto_now=True)`

# --- AWS Setup ---
s3 = boto3.client("s3", region_name="ap-southeast-1")
bucket_name = "bjj-video-storage"
cloudfront_base_url = "https://d1dia18owflx7r.cloudfront.net"

# --- Local folder ---
local_folder = Path("/Users/quanefiom/desktop/bjj_videos")

# --- Sanitize filename for S3 ---
def sanitize_filename(name):
    return re.sub(r"[^a-zA-Z0-9/_\.-]", "_", name)

# --- Upload & Save ---
def upload_filtered_videos(folder: Path):
    for local_path in folder.rglob("*.mp4"):
        if not local_path.name.startswith("-"):
            continue  # Skip files not starting with "-"

        relative_path = local_path.relative_to(folder)
        sanitized_path = sanitize_filename(str(relative_path))
        cloudfront_url = f"{cloudfront_base_url}/{sanitized_path}"  # ✅ Clean URL (no ?v=)

        # --- Check S3 ---
        exists_in_s3 = False
        try:
            s3.head_object(Bucket=bucket_name, Key=sanitized_path)
            print(f"⏭️ Skipping upload (already in S3): {sanitized_path}")
            exists_in_s3 = True
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                print(f"❌ Error checking S3: {sanitized_path}: {e}")
                continue

        # --- Upload if not in S3 ---
        if not exists_in_s3:
            try:
                print(f"📤 Uploading: {sanitized_path}")
                s3.upload_file(
                    str(local_path),
                    bucket_name,
                    sanitized_path,
                    ExtraArgs={
                        "ContentType": "video/mp4",
                        "CacheControl": "max-age=31536000, public",
                    },
                )
                print(f"✅ Uploaded: {cloudfront_url}")
            except Exception as e:
                print(f"❌ Failed to upload {local_path.name}: {e}")
                continue

        # --- Save or Update DB ---
        try:
            title = local_path.stem.replace("_", " ").replace("-", " ").title()

            video, created = Video.objects.update_or_create(
                video_url=cloudfront_url,  # ✅ Always save clean URL
                defaults={"title": title},
            )

            if created:
                print(f"✅ Saved new video: {title} → {cloudfront_url}")
            else:
                print(f"🔄 Updated existing video: {title} → {cloudfront_url}")

        except Exception as e:
            print(f"❌ Failed to save to DB: {e}")

    print("\n🎉 Upload & DB save completed.")


# --- Run Script ---
if __name__ == "__main__":
    upload_filtered_videos(local_folder)
