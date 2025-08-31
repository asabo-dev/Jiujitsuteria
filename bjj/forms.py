"""
This module handles video uploads to S3 and saves metadata in the database.
It uses Django forms to validate and process the upload.
It sanitizes file paths to ensure they are S3-compatible.
It uploads to AWS S3 and serves through CloudFront.
"""

import re
import boto3
from django import forms
from django.conf import settings
from botocore.exceptions import ClientError
from .models import Video


# --- AWS Setup ---
s3 = boto3.client("s3", region_name="ap-southeast-1")  # adjust if needed
BUCKET_NAME = "bjj-video-storage"


def sanitize_path(path: str) -> str:
    """Make a path S3-safe (alphanumeric, _, ., -, / allowed)."""
    return re.sub(r"[^a-zA-Z0-9/_\.-]", "_", path)


class VideoUploadForm(forms.ModelForm):
    file = forms.FileField(required=True)

    class Meta:
        model = Video
        fields = ["title", "guard", "position", "technique", "tags"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        uploaded_file = self.cleaned_data["file"]

        # ✅ Build path: Category/SubCategory/filename
        if instance.guard:
            key = f"Guard/{instance.guard.name}/{uploaded_file.name}"
        elif instance.position:
            key = f"Position/{instance.position.name}/{uploaded_file.name}"
        elif instance.technique:
            key = f"Technique/{instance.technique.name}/{uploaded_file.name}"
        else:
            key = f"Uncategorized/{uploaded_file.name}"

        key = sanitize_path(key)

        # ✅ Upload to S3
        try:
            s3.upload_fileobj(
                uploaded_file,
                BUCKET_NAME,
                key,
                ExtraArgs={
                    "ContentType": "video/mp4",
                    "CacheControl": "max-age=31536000, public",
                },
            )
        except Exception as e:
            raise forms.ValidationError(f"❌ Failed to upload video to S3: {e}")

        # ✅ Use CloudFront URL (clean, no ?v=)
        cloudfront_domain = getattr(settings, "CLOUDFRONT_DOMAIN", "")
        if not cloudfront_domain:
            raise forms.ValidationError("CloudFront domain is not configured in settings.")

        clean_url = f"{cloudfront_domain}/{key}"

        # ✅ Save or update DB entry (no duplicates)
        video, created = Video.objects.update_or_create(
            video_url=clean_url,
            defaults={
                "title": instance.title,
                "guard": instance.guard,
                "position": instance.position,
                "technique": instance.technique,
            },
        )

        if commit:
            video.save()
            self.save_m2m()
            # ✅ Save tags (many-to-many)
            if "tags" in self.cleaned_data:
                video.tags.set(self.cleaned_data["tags"])

        return video
