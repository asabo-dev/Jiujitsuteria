from django.contrib import admin
from .models import Video, Position, Technique, Guard, Tag

admin.site.register(Video)
admin.site.register(Position)
admin.site.register(Technique)
admin.site.register(Guard)
admin.site.register(Tag)
