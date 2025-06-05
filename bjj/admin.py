from django.contrib import admin

# Register your models here.
from .models import Position, Technique, Guard

admin.site.register(Position)
admin.site.register(Technique)
admin.site.register(Guard)