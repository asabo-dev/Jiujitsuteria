"""
Sync thumbnails in DB with files already in the public S3 bucket.
"""

import os
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from django.conf import settings
from bjj.models import Video


class Command(BaseCommand):
    help = "Sync DB thumbnail_url with existing JPGs in the public CloudFront domain"

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only update videos with no thumbnail_url set",
        )

    def handle(self, *args, **options):
        public_cdn = settings.CLOUDFRONT_PUBLIC_DOMAIN  # d3ix9aup7044ea.cloudfront.net
        only_missing = options["only_missing"]
        updated = 0

        for video in Video.objects.all():
            try:
                # Skip if only_missing is set and video already has a thumbnail
                if only_missing and video.thumbnail_url:
                    continue

                parsed = urlparse(video.video_url)
                key = parsed.path.lstrip("/")   # e.g. Guard/Butterfly_Guard/collar_drag.mp4
                base, _ = os.path.splitext(key)
                thumb_key = f"{base}.jpg"
                public_url = f"https://{public_cdn}/{thumb_key}"

                if video.thumbnail_url != public_url:
                    video.thumbnail_url = public_url
                    video.save(update_fields=["thumbnail_url"])
                    updated += 1
                    self.stdout.write(f"✅ Updated thumbnail for {video.title}")

            except Exception as e:
                self.stdout.write(f"❌ Skipped {video.title}: {e}")

        self.stdout.write(f"🎉 Done! {updated} thumbnails updated in DB.")
