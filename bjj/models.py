# Create your models here.

from django.db import models
class Position(models.Model):
    position_name = models.CharField(max_length=100)  # e.g. "Mount", "Side Control", "Standing"

    def __str__(self):
        return self.position_name
class Technique(models.Model):
    technique_name = models.CharField(max_length=100)  # e.g. "Sweep", "Escape", "Submission"
    
    def __str__(self):
        return self.technique_name
class Guard(models.Model):
    guard_name = models.CharField(max_length=100)  # e.g. "Closed Guard", "Dela Riva", "Butterfly"

    def __str__(self):
        return self.guard_name
    
class Video(models.Model):
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    description = models.TextField(blank=True, null=True)

    # Foreign Keys for categorization
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    technique = models.ForeignKey(Technique, on_delete=models.SET_NULL, null=True, blank=True)
    guard = models.ForeignKey(Guard, on_delete=models.SET_NULL, null=True, blank=True)

    # Optional: allow users to tag with multiple guards, techniques, or positions
    tags = models.ManyToManyField('Tag', blank=True)

    def __str__(self):
        return self.title
    
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)  # For additional tagging flexibility

    def __str__(self):
        return self.name