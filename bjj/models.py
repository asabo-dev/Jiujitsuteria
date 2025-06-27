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
        Replace the S3 bucket prefix in the video_url with the CloudFront domain
        defined in settings.py.
        """
        s3_prefix = " https://jiujitsuteria-videos.s3.amazonaws.com"  # 🔁 Replace this with your actual S3 bucket URL
        cloudfront_domain = getattr(settings, 'CLOUDFRONT_DOMAIN', '')
        return self.video_url.replace(s3_prefix, f"{cloudfront_domain}/")
