"""Django models for managing BJJ videos.
Development uses local video storage, while production uses
CloudFront for video and thumbnail delivery.
"""

from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.db import models

from jiujitsuteria.utils.cloudfront import generate_signed_url


class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Technique(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Guard(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    title = models.CharField(max_length=200)

    # Existing database field containing the production video URL.
    # Development uses only the filename to locate the local video.
    video_url = models.URLField(
        help_text="CloudFront URL for the video file in production."
    )

    # Existing database field containing the production thumbnail URL.
    # Thumbnails are not currently available in local development.
    thumbnail_url = models.URLField(
        blank=True,
        null=True,
        help_text="CloudFront URL for the thumbnail in production."
    )

    tags = models.ManyToManyField(
        "Tag",
        related_name="videos",
        blank=True
    )

    position = models.ForeignKey(
        "Position",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    technique = models.ForeignKey(
        "Technique",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    guard = models.ForeignKey(
        "Guard",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    # -----------------------------
    # Get video filename
    # -----------------------------
    @staticmethod
    def _get_video_filename(url):
        """Get the filename from the stored production URL."""
        if not url:
            return None

        return Path(urlparse(url).path).name

    # -----------------------------
    # Video URL
    # -----------------------------
    @property
    def signed_video_url(self):
        """Return a local video URL in development or a signed
        CloudFront URL in production.
        """
        if not self.video_url:
            return None

        # Development: find the video in local storage.
        if settings.DEBUG:
            filename = self._get_video_filename(self.video_url)

            if not filename:
                return None

            matches = list(
                Path(settings.MEDIA_ROOT).rglob(filename)
            )

            if not matches:
                return None

            relative_path = matches[0].relative_to(
                settings.MEDIA_ROOT
            )

            return f"{settings.MEDIA_URL}{relative_path.as_posix()}"

        # Production: use the original CloudFront path.
        path = urlparse(self.video_url).path.lstrip("/")

        return generate_signed_url(path, expires_in=3600)

    # -----------------------------
    # Thumbnail URL
    # -----------------------------
    @property
    def local_thumbnail_url(self):
        """Return no thumbnail in development and the stored
        CloudFront URL in production.
        """
        if settings.DEBUG:
            return None

        return self.thumbnail_url

    # -----------------------------
    # Unsigned CloudFront fallback
    # -----------------------------
    def cloudfront_url(self):
        """Return the stored video URL without signing it."""
        return self.video_url