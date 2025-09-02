from django.contrib import admin
from django.utils.html import format_html
from .models import Video, Position, Technique, Guard, Tag


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_link')
    
    def video_link(self, obj):
        url = obj.cloudfront_url() if callable(obj.cloudfront_url) else obj.cloudfront_url
        if url:
            return format_html('<a href="{}" target="_blank">View Video</a>', url)
        return "No video"
    video_link.short_description = 'CloudFront Video'


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
