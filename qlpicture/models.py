# coding=utf-8
"""
千里项目中涉及到图片存储和操作的类集合.
目前实现的类有:
TalkPicture - 用以接受用户发送的图片,从而实现通话过程中的图片发送功能.
"""

from django.db import models
from django.core.cache import cache
from mysite import settings

import uuid
import os
import time
import random

# Create your models here.

def get_path(instance, filename):
    """返回包含有通过uuid定义的图片文件名的路径"""
    # 读取图片类型
    ext = filename.split('.')
    if len(ext) > 1:
        ext = ext[-1]
    else:
        ext = ''
    # 随机生成文件名
    filename = uuid.uuid1().hex + '.' + ext
    # 根据当前日期生成文件夹名
    directory_name = time.strftime('%Y%m%d',time.localtime(time.time()))
    # 随机生成一个文件夹名
    second_directory_name = str(random.randint(1, 50))
    return os.path.join(settings.MEDIA_ROOT, 'picture', directory_name, second_directory_name, filename)

class TalkPicture(models.Model):
    """临时存储用户在对话时发送的图片"""
    picture = models.ImageField('图片', upload_to=get_path)
    send_from = models.CharField('发送者是', max_length=254, null=True,
                                 blank=True)
    send_to = models.CharField('接收者为', max_length=254, null=True,
                               blank=True)
    # 不需要从QLUser处链接回来,因为仅仅是临时的图片
    # 为了提供存储速度(不需要确认外键的数值),而且单纯为了记录,采用char来记录即可
    # send_from = models.ForeignKey('qluser.QLUser', related_name='+', null=True)
    # send_to = models.ForeignKey('qluser.QLUser', related_name='+', null=True)
    send_date = models.DateTimeField('发送时间', auto_now_add=True)
    # 加上标志位判断该图片是否已删除
    is_available = models.BooleanField('是否可用', default=True, db_index=True)

    def __unicode__(self):
        return self.picture.name

class SessionPicture(models.Model):
    """存储用户在对话中发送的图片,根据方案1进行了改进"""
    picture = models.ImageField("图片", upload_to=get_path, null=True, blank=True)
    session_id = models.CharField("Session ID", db_index=True, max_length=64)
    index = models.PositiveSmallIntegerField("图片序号", db_index=True)

    send_date = models.DateTimeField('发送时间', auto_now_add=True)
    # 加上标志位判断该图片是否已删除
    is_available = models.BooleanField('是否可用', default=True, db_index=True)

    send_from = models.CharField('发送者是', max_length=254, null=True,
                                 blank=True)
    send_to = models.CharField('接收者为', max_length=254, null=True,
                               blank=True)

    def __unicode__(self):
        return ''.join([str(self.session_id),'+',str(self.index),'+',self.picture.name])

    def save(self, *args, **kwargs):
        # 在把image存在硬盘前存入Memcache中
        image_data = self.picture.read()
        # 命名原则： [session_id]:[index]
        image_key = self.session_id + ":" + str(self.index)
        cache.set(image_key, image_data, 20)

        super(SessionPicture, self).save(*args, **kwargs) 


class SessionPictureInformation(models.Model):
    """存储用户在对话中发送的图片的信息,如当前图片总数等,根据方案1进行了改进"""
    session_id = models.CharField("对话唯一标识", db_index=True, unique=True, max_length=64)
    # 便于处理在client端处理图片序号从0开始,最大图片序号就等于目前图片总数-1
    # 当前图片数量,不是最大序号
    maximum_index = models.PositiveSmallIntegerField("图片数目", default=0)

    def __unicode__(self):
        return str(self.session_id)