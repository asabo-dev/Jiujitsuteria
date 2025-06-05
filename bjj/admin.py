from django.contrib import admin

# Register your models here.
from .models import Position, Technique, Guard, Video, Tag

admin.site.register(Position)
admin.site.register(Technique)
admin.site.register(Guard)
admin.site.register(Video)
admin.site.register(Tag)