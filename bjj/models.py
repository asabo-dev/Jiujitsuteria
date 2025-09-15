"""Django models for managing BJJ Web App videos,
with private video access via CloudFront signed URLs
and public thumbnails served via a separate CloudFront distribution."""

from django.db import models
from django.conf import settings
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

    # Video file (stored in private S3 bucket, requires signed URL)
    video_url = models.URLField(
        help_text="CloudFront or S3 URL to the video file (private bucket)"
    )

    # Thumbnail image (stored in public S3 bucket, no signing required)
    thumbnail_url = models.URLField(
        blank=True,
        null=True,
        help_text="CloudFront URL to the thumbnail image (public bucket)"
    )

    tags = models.ManyToManyField('Tag', related_name='videos', blank=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True)
    technique = models.ForeignKey('Technique', on_delete=models.SET_NULL, null=True, blank=True)
    guard = models.ForeignKey('Guard', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    # -----------------------------
    # CloudFront signed video URL
    # -----------------------------
    @property
    def signed_video_url(self):
        """Return a CloudFront signed URL for the video file."""
        if not self.video_url:
            return None
        path = self.video_url.split(f"{settings.CLOUDFRONT_DOMAIN}/")[-1]
        return generate_signed_url(path, expires_in=3600)

    # -----------------------------
    # Unsigned fallback (rarely used)
    # -----------------------------
    def cloudfront_url(self):
        """Return an unsigned CloudFront URL as a fallback."""
        return self.video_url
