"""
Django management command to generate thumbnails for videos stored in S3
and update their records with CloudFront public URLs.
"""

import os
import tempfile
import boto3
import subprocess
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from django.conf import settings
from bjj.models import Video


class Command(BaseCommand):
    help = "Generate thumbnails for all videos and upload to public S3 bucket, updating DB"

    def handle(self, *args, **options):
        s3_client = boto3.client("s3")

        private_bucket = settings.AWS_PRIVATE_VIDEO_BUCKET  # your private videos bucket
        public_bucket = settings.AWS_PUBLIC_THUMBNAIL_BUCKET  # jiujitsuteria-mediia
        public_cdn = settings.CLOUDFRONT_PUBLIC_DOMAIN       # d3ix9aup7044ea.cloudfront.net

        videos = Video.objects.all()
        self.stdout.write(f"🔹 Processing {videos.count()} videos for thumbnails...")

        for video in videos:
            try:
                self.stdout.write(f"📹 Processing: {video.title}")

                # Extract video key from its URL (private bucket)
                parsed = urlparse(video.video_url or "")
                s3_key = parsed.path.lstrip("/") if parsed.path else None

                if not s3_key:
                    self.stdout.write(f"❌ Skipping {video.title}: no valid S3 key")
                    continue

                # Download video temporarily
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
                    s3_client.download_file(private_bucket, s3_key, temp_video.name)
                    temp_video_path = temp_video.name

                # Generate thumbnail with ffmpeg
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_thumb:
                    thumb_path = temp_thumb.name

                subprocess.run(
                    [
                        "ffmpeg",
                        "-i", temp_video_path,
                        "-ss", "00:00:01.000",  # capture frame at 1s
                        "-vframes", "1",
                        "-vf", "scale=320:-1",  # width=320px, keep aspect ratio
                        thumb_path,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                # Define thumbnail key in public bucket
                thumbnail_key = f"thumbnails/{os.path.splitext(s3_key)[0]}.jpg"

                # Upload to public bucket
                s3_client.upload_file(
                    thumb_path,
                    public_bucket,
                    thumbnail_key,
                    ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"},
                )

                # Build public CloudFront URL
                public_url = f"https://{public_cdn}/{thumbnail_key}"

                # Save thumbnail URL in DB (always update)
                video.thumbnail_url = public_url
                video.save(update_fields=["thumbnail_url"])

                self.stdout.write(f"✅ Thumbnail updated for {video.title}")

                # Cleanup temp files
                os.remove(temp_video_path)
                os.remove(thumb_path)

            except Exception as e:
                self.stdout.write(f"❌ Failed {video.title}: {e}")

        self.stdout.write("🎉 Thumbnail generation complete. All thumbnails uploaded & DB updated!")
