# coding=utf-8
from django.db import models

# Create your models here.

class QLFriend(models.Model):
    """
    存储用户的千里好友列表
    主要用于正确显示来电通知中的姓名
    """
    user_number = models.CharField('用户号码', max_length=20, db_index=True)
    friend_number = models.CharField('好友号码', max_length=20, db_index=True)
    friend_name = models.CharField('好友名字', max_length=128)

    def __unicode__(self):
        return self.user_number + '-' + self.friend_number