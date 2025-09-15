"""Admin configuration for BJJ video management with signed/unsigned
CloudFront URL testing, previews, and status indicators."""

from django.contrib import admin
from django.utils.html import format_html
from .models import Video, Position, Technique, Guard, Tag


# -----------------------------
# Video Admin
# -----------------------------
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'signed_status',
        'thumbnail_status',
        'signed_video_link',
        'unsigned_video_link',
        'video_preview',
        'thumbnail_preview',
    )
    readonly_fields = (
        'signed_video_link',
        'unsigned_video_link',
        'video_preview',
        'thumbnail_preview',
    )
    list_filter = (
        'position',
        'technique',
        'guard',
        'tags',
    )
    search_fields = ('title',)

    # -----------------------------
    # Status Columns
    # -----------------------------
    def signed_status(self, obj):
        """Show ✔️ or ❌ for signed video URL status."""
        if obj.signed_video_url:
            return format_html('<span style="color:green;">✔ Signed</span>')
        return format_html('<span style="color:red;">❌ Missing</span>')
    signed_status.short_description = "Video Status"

    def thumbnail_status(self, obj):
        """Show ✔️ or ❌ for thumbnail URL status (public)."""
        if obj.thumbnail_url:
            return format_html('<span style="color:green;">✔ Available</span>')
        return format_html('<span style="color:red;">❌ Missing</span>')
    thumbnail_status.short_description = "Thumbnail Status"

    # -----------------------------
    # Signed Video
    # -----------------------------
    def signed_video_link(self, obj):
        url = obj.signed_video_url
        if url:
            return format_html('<a href="{}" target="_blank">Signed Video</a>', url)
        return "No signed video"
    signed_video_link.short_description = 'Signed Video Link'

    # -----------------------------
    # Unsigned Video
    # -----------------------------
    def unsigned_video_link(self, obj):
        url = obj.cloudfront_url()
        if url:
            return format_html('<a href="{}" target="_blank">Unsigned Video</a>', url)
        return "No unsigned video"
    unsigned_video_link.short_description = 'Unsigned Video Link'

    # -----------------------------
    # Video Preview
    # -----------------------------
    def video_preview(self, obj):
        url = obj.signed_video_url
        if url:
            return format_html('<video src="{}" width="300" controls></video>', url)
        return "No video preview"
    video_preview.short_description = 'Video Preview (Signed)'

    # -----------------------------
    # Thumbnail Preview
    # -----------------------------
    def thumbnail_preview(self, obj):
        url = obj.thumbnail_url
        if url:
            return format_html('<img src="{}" width="150" style="border-radius:8px;" />', url)
        return "No thumbnail"
    thumbnail_preview.short_description = 'Thumbnail Preview'


# -----------------------------
# Other Models
# -----------------------------
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Technique)
class TechniqueAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Guard)
class GuardAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
