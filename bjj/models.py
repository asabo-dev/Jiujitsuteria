from django.db import models
from django.conf import settings
from django.utils.text import slugify

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

    tags = models.ManyToManyField('Tag', related_name='videos', blank=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True)
    technique = models.ForeignKey('Technique', on_delete=models.SET_NULL, null=True, blank=True)
    guard = models.ForeignKey('Guard', on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.title

    def cloudfront_url(self):
        """
        Replace the S3 URL prefix with your CloudFront domain.
        """
        s3_prefix = "https://bjj-video-storage.s3.ap-southeast-1.amazonaws.com"
        cloudfront_domain = getattr(settings, 'CLOUDFRONT_DOMAIN', '')
        if self.video_url.startswith(s3_prefix) and cloudfront_domain:
            return self.video_url.replace(s3_prefix, cloudfront_domain)
        return self.video_url
