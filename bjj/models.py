# Create your models here.

from django.db import models
class Position(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Mount", "Side Control", "Standing"

    def __str__(self):
        return self.name
class Technique(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Sweep", "Escape", "Submission"

    def __str__(self):
        return self.name
class Guard(models.Model):
    name = models.CharField(max_length=100)  # e.g. "Closed Guard", "Dela Riva", "Butterfly"

    def __str__(self):
        return self.name