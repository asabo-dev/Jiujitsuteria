"""Django models for managing BJJ videos.
Development uses local video storage, while production uses
CloudFront for video and thumbnail delivery.
"""

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
    # Development converts this URL to a local media path.
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
    # Extract file path from URL
    # -----------------------------
    @staticmethod
    def _get_media_path(url):
        """Extract the file path from a stored URL."""
        if not url:
            return None

        return urlparse(url).path.lstrip("/")

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

        path = self._get_media_path(self.video_url)

        # Development: serve video from local MEDIA_ROOT.
        if settings.DEBUG:
            return f"{settings.MEDIA_URL}{path}"

        # Production: serve video through signed CloudFront URL.
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