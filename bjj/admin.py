from django.contrib import admin

# Register your models here.
from .models import Position, Technique, Guard, Video, Tag
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['position_name']
@admin.register(Technique)
class TechniqueAdmin(admin.ModelAdmin):
    list_display = ['technique_name']
@admin.register(Guard)
class GuardAdmin(admin.ModelAdmin):
    list_display = ['guard_name']
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_url', 'description', 'position', 'technique', 'guard']
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

