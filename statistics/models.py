# coding=utf-8
from django.db import models

# Create your models here.

class Stats(models.Model):
    number_active_user = models.IntegerField(default=0)
    number_sesiion = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    month = models.IntegerField(default=0)
    day = models.IntegerField(default=0)
    hour = models.IntegerField(default=0)
    sent = models.NullBooleanField(default=False)
    
    def __unicode__(self):
        return self.number_active_user