"""
Uploads videos starting with '-' to private S3, generates thumbnails,
uploads them to public S3 (only if missing), and updates Django DB
with clean CloudFront URLs.

✅ Consistent with .env.dev AWS credentials
✅ Dry-run mode available
✅ Only processes files starting with '-'
✅ Skips existing thumbnails
"""

import os
import re
import sys
import tempfile
import subprocess
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
import django

# --- Toggle dry-run mode ---
DRY_RUN = False  # Set to True to test without uploading

# --- Setup Django Environment ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jiujitsuteria.settings.dev")
django.setup()

from bjj.models import Video
from django.conf import settings

# --- AWS Credentials & Buckets from settings ---
AWS_REGION = settings.AWS_S3_REGION_NAME
PRIVATE_BUCKET = settings.AWS_PRIVATE_VIDEO_BUCKET
PUBLIC_BUCKET = settings.AWS_PUBLIC_THUMBNAIL_BUCKET
CLOUDFRONT_VIDEO_DOMAIN = f"https://{settings.CLOUDFRONT_DOMAIN}"
CLOUDFRONT_THUMBNAIL_DOMAIN = f"https://{settings.CLOUDFRONT_PUBLIC_DOMAIN}"

# --- AWS S3 client ---
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

# --- Local folder containing videos ---
LOCAL_FOLDER = Path("/Users/quanefiom/desktop/bjj_videos")

# --- Helper: sanitize filename for S3 ---
def sanitize_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9/_\.-]", "_", name)

# --- Helper: generate thumbnail locally (fast seek) ---
def generate_thumbnail(video_path: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_thumb:
        thumb_path = tmp_thumb.name

    cmd = [
        "ffmpeg",
        "-y",                  # overwrite if temp file exists
        "-ss", "1",            # seek to 1 second
        "-i", video_path,
        "-frames:v", "1",      # grab 1 frame
        "-vf", "scale=320:-1", # resize
        "-f", "image2",
        thumb_path,
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return thumb_path


# --- Upload videos + thumbnails and update DB ---
def upload_videos(folder: Path):
    for local_path in folder.rglob("*.mp4"):
        # Only process files that start with "-"
        if not local_path.name.startswith("-"):
            continue

        # S3 path
        relative_path = local_path.relative_to(folder)
        sanitized_path = sanitize_filename(str(relative_path))

        # CloudFront URLs
        cloudfront_url = f"{CLOUDFRONT_VIDEO_DOMAIN}/{sanitized_path}"
        thumbnail_key = f"{os.path.splitext(sanitized_path)[0]}.jpg"
        thumbnail_url = f"{CLOUDFRONT_THUMBNAIL_DOMAIN}/{thumbnail_key}"

        print(f"\n🔹 Processing: {local_path.name}")
        print(f"Video S3 key: {sanitized_path}")
        print(f"Thumbnail S3 key: {thumbnail_key}")

        if not DRY_RUN:
            # --- Upload video to private bucket ---
            try:
                s3.head_object(Bucket=PRIVATE_BUCKET, Key=sanitized_path)
                print(f"⏭️ Video exists in S3, skipping: {sanitized_path}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    s3.upload_file(
                        str(local_path),
                        PRIVATE_BUCKET,
                        sanitized_path,
                        ExtraArgs={
                            "ContentType": "video/mp4",
                            "CacheControl": "max-age=31536000, public",
                        },
                    )
                    print(f"✅ Uploaded video: {cloudfront_url}")
                else:
                    print(f"❌ Error checking video in S3: {e}")
                    continue

            # --- Generate thumbnail ---
            try:
                thumb_path = generate_thumbnail(str(local_path))
            except Exception as e:
                print(f"❌ Failed to generate thumbnail for {local_path.name}: {e}")
                continue

            # --- Upload thumbnail to public bucket (skip if exists) ---
            try:
                s3.head_object(Bucket=PUBLIC_BUCKET, Key=thumbnail_key)
                print(f"⏭️ Thumbnail exists in S3, skipping: {thumbnail_key}")
                os.remove(thumb_path)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    s3.upload_file(
                        thumb_path,
                        PUBLIC_BUCKET,
                        thumbnail_key,
                        ExtraArgs={"ContentType": "image/jpeg"},
                    )
                    print(f"✅ Uploaded thumbnail: {thumbnail_url}")
                    os.remove(thumb_path)
                else:
                    print(f"❌ Error checking thumbnail in S3: {e}")
                    os.remove(thumb_path)
                    continue

            # --- Save / update Django DB (improved hybrid logic) ---
            try:
                title = local_path.stem.replace("_", " ").replace("-", " ").title()

                video, created = Video.objects.update_or_create(
                    video_url=cloudfront_url,  # ✅ always clean & consistent
                    defaults={
                        "title": title,
                        "thumbnail_url": thumbnail_url,
                    },
                )

                if created:
                    print(f"✅ Saved new video in DB: {title} → {cloudfront_url}")
                else:
                    print(f"🔄 Updated existing video in DB: {title} → {cloudfront_url}")

            except Exception as e:
                print(f"❌ Failed to save video {local_path.name} to DB: {e}")

        else:
            # Dry-run: print actions without performing them
            print(f"[DRY-RUN] Would upload video to private S3: {sanitized_path}")
            print(f"[DRY-RUN] Would generate thumbnail and upload to public S3: {thumbnail_key}")
            title = local_path.stem.replace("_", " ").replace("-", " ").title()
            print(f"[DRY-RUN] Would save/update DB: {title} → {cloudfront_url}")

    print(f"\n🎉 All eligible videos processed (Dry-run mode: {DRY_RUN})")


# --- Run script ---
if __name__ == "__main__":
    upload_videos(LOCAL_FOLDER)
