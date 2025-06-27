# Create your models here.

from django.db import models
from django.conf import settings

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
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    tags = models.ManyToManyField('Tag', related_name='videos')

    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True)
    technique = models.ForeignKey('Technique', on_delete=models.SET_NULL, null=True, blank=True)
    guard = models.ForeignKey('Guard', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    def cloudfront_url(self):
        """
        Replaces the S3 URL prefix with the CloudFront distribution domain.
        Assumes videos are served using CloudFront.
        """
        s3_prefix = "https://jiujitsuteria-videos.s3.amazonaws.com"
        cloudfront_domain = getattr(settings, 'CLOUDFRONT_DOMAIN', '')
        if self.video_url.startswith(s3_prefix):
            return self.video_url.replace(s3_prefix, cloudfront_domain)
        return self.video_url