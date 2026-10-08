"""
Sync local BJJ video files with the Django Video database.

Purpose:
- Scan the local bjj_videos folder for video files.
- Create Video database records for files that are not already registered.
- Leave existing Video records unchanged.
- This command is for local development only.
- New videos can then be edited and labeled through Django Admin.

Production files and the existing CloudFront/S3 setup are not modified.
"""

from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bjj.models import Video


class Command(BaseCommand):
    help = "Create Video records for local files not yet in the database."

    def handle(self, *args, **options):
        # This command is only for local development.
        if not settings.DEBUG:
            raise CommandError(
                "This command is only available in development."
            )

        media_root = Path(settings.MEDIA_ROOT)

        # Check that the local video folder exists.
        if not media_root.is_dir():
            raise CommandError(
                f"Video folder not found: {media_root}"
            )

        # Video file types to scan for.
        extensions = {".mp4", ".mov", ".webm", ".m4v"}

        # Get filenames already registered in the database.
        existing_filenames = {
            Path(urlparse(url).path).name
            for url in Video.objects.values_list("video_url", flat=True)
            if url
        }

        created = 0
        skipped = 0

        # Scan the video folder and all subfolders.
        for path in sorted(media_root.rglob("*")):

            if not path.is_file():
                continue

            if path.suffix.lower() not in extensions:
                continue

            # Do not create a duplicate database record.
            if path.name in existing_filenames:
                skipped += 1
                continue

            # Store the relative path in the existing video_url field.
            relative_path = path.relative_to(media_root).as_posix()

            Video.objects.create(
                title=path.stem,
                video_url=f"https://local.invalid/{relative_path}",
            )

            existing_filenames.add(path.name)
            created += 1

            self.stdout.write(
                f"Created: {path.name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Created {created} records; "
                f"skipped {skipped} existing filenames."
            )
        )
