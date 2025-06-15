# Create your models here.

from django.db import models

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
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.SET_NULL, null=True, blank=True)
    guard = models.ForeignKey(Guard, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title
