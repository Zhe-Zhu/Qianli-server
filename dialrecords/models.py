#coding=utf-8
from django.db import models

# Create your models here.

class MissedCalls(models.Model):
    """
    Store missed calls.
    When users open [Recent calls], they can fetch missed calls from server.
    """
    called_number = models.CharField('被叫号码', max_length=20, db_index=True)
    calling_number = models.CharField('呼叫号码', max_length=20, db_index=True)
    calling_type = models.CharField('记录类型', max_length=1)
    calling_date = models.DateTimeField('呼叫时间', auto_now_add=True)

    def __unicode__(self):
        return self.called_number

    