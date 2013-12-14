# coding=utf-8
from django.db import models

# Create your models here.
class BetaUserEmail(models.Model):
    email = models.EmailField(
        '邮件地址', max_length=254)
    join_date = models.DateTimeField('加入时间', auto_now_add=True)

    def __unicode__(self):
        return self.email