from django.db import models

# Create your models here.

class UserInfo(models.Model):
    name = models.CharField(max_length=60)
    token = models.CharField(max_length=128)
    lastregtime = models.DateTimeField()

    def __unicode__(self):
        return self.name

class LastFeedback(models.Model):
    name = models.CharField(max_length=60)
    lastfeedback = models.DateTimeField()

    def __unicode__(self):
        return self.name
