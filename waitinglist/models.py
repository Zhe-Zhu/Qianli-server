# coding=utf-8
from django.db import models

# Create your models here.

class Waitinglist(models.Model):
    number = models.CharField(max_length=60)
    udid = models.CharField(max_length=128)
    partner = models.CharField(max_length=60)
    partner_udid = models.CharField(max_length=128)
    partner_verified = models.NullBooleanField(default=False)
    
    def __unicode__(self):
        return self.number

class Waitedlist(models.Model):
    number = models.CharField(max_length=60)
    udid = models.CharField(max_length=128)
    verified = models.NullBooleanField(default=False)
    
    def __unicode__(self):
        return self.number
