# coding=utf-8
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager)
from django.utils import timezone
from mysite import settings

import uuid
import os
import random

# Create your models here.

class QLUserManager(BaseUserManager):
    """重写了创建用户的函数"""

    def create_user(self, udid, name, os_type, avatar, phone_number, email):
        now = timezone.now()
        if not udid:
            raise ValueError('必须要提供udid')
        if (phone_number or email) is None:
            raise ValueError('手机号和邮箱必须要提供一个')
        if name is None or name is '':
            raise ValueError('名字不能为空')
        if os_type is None or os_type is '':
            raise ValueError('系统类型不能为空')
        if os_type not in ('i', 'a', 'o'):
            raise ValueError('系统类型%s输入错误' % os_type)
        # TODO 输入类型检查

        # TODO 检验头像,如果没能上传头像则使用默认头像
        # TODO 验证头像的有效性
        # imageField只是一个string,需要手动把传过来的图像存起来
        if avatar is None:
            avatar = 'default_avatar.jpg'

        email = QLUserManager.normalize_email(email)
        user = self.model(
            udid=udid, phone_number=phone_number, email=email, name=name, os_type=os_type,
            avatar=avatar, is_staff=False, is_active=True, is_superuser=False, last_login=now)
        user.set_password('Qianli') # 先暂时设置一个默认密码
        user.save(using=self._db)
        return user

    # create_superuser 似乎在我们的场景内不需要
    def create_superuser(self, udid, avatar, name, os_type, phone_number):
        user = self.create_user(udid=udid, avatar=avatar, name=name, os_type=None, phone_number=None, email=None)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class QLUserInformationUpdate(models.Model):
    """记录用户是否更新了个人资料, 便于别的用户拉取新的信息"""
    phone_number = models.CharField('手机号码', max_length=20, null=True, blank=True, unique=True)
    update_time = models.PositiveSmallIntegerField('更新次数', default=0)

def get_path_avatar(instance, filename):
    """
    返回包含有通过uuid定义的随机图片文件名的路径
    用于存储用户头像
    客户端需要通过phone_number拿到头像文件名才能调用相关API拿到头像图片数据
    """
    # 读取图片类型
    ext = filename.split('.')
    if len(ext) > 1:
        ext = ext[-1]
    else:
        ext = ''
    # 随机生成文件名
    filename = uuid.uuid1().hex
    filename_jpg = ''.join([filename, '.', 'jpg'])
    filename_jpeg = ''.join([filename, '.', 'jpeg'])
    filename_png = ''.join([filename, '.', 'png'])
    # 确保filename的唯一性
    while os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'avatar', filename_jpg)) or os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'avatar', filename_jpeg)) or os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'avatar', filename_png)):
        filename = uuid.uuid1().hex

    filename_ext = filename + '.' + ext
    # 随机生成一个文件夹名
    second_directory_name = str(random.randint(1, 100))    
    return os.path.join(settings.MEDIA_ROOT, 'avatar', second_directory_name, filename_ext)

def get_path_large_avatar(instance, filename):
    """
    返回包含有通过uuid定义的随机图片文件名的路径
    用于存储用户头像
    客户端需要通过phone_number拿到头像文件名才能调用相关API拿到头像图片数据
    """
    # 读取图片类型
    ext = filename.split('.')
    if len(ext) > 1:
        ext = ext[-1]
    else:
        ext = ''
    # 随机生成文件名
    filename = uuid.uuid1().hex + '_large'
    filename_jpg = ''.join([filename, '.', 'jpg'])
    filename_jpeg = ''.join([filename, '.', 'jpeg'])
    filename_png = ''.join([filename, '.', 'png'])
    # 确保filename的唯一性
    while os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'avatar', filename_jpg)) or os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'avatar', filename_jpeg)) or os.path.isfile(os.path.join(settings.MEDIA_ROOT, 'avatar', filename_png)):
        filename = uuid.uuid1().hex + '_large'

    filename_ext = filename + '.' + ext
    # 随机生成一个文件夹名
    second_directory_name = str(random.randint(1, 100))    
    return os.path.join(settings.MEDIA_ROOT, 'avatar', second_directory_name, filename_ext)

class QLUser(AbstractBaseUser, PermissionsMixin):
    """在原Django抽象用户类的基础上添加了我们需要记录的信息,如udid等"""

    # 每个设备的唯一标识,用以区分不同的用户
    udid = models.CharField(
        '设备标识码', max_length=128, unique=True, db_index=True)

    phone_number = models.CharField(
        '手机号码', max_length=20, null=True, blank=True, unique=True)
    email = models.EmailField(
        '邮件地址', max_length=254, null=True, blank=True)
    name = models.CharField('昵称', max_length=120)
    os_type = models.CharField('系统类型', max_length=20, default="i"
    )

    # 头像文件名应用udid来命名,保证唯一性
    avatar = models.ImageField(
        '头像', upload_to=get_path_avatar, blank=True, null=True)
    large_avatar = models.ImageField(
        '拨号时头像', upload_to=get_path_large_avatar, blank=True, null=True)    

    USERNAME_FIELD = 'udid'
    REQUIRED_FIELDS = ['name', 'phone_number', 'email', 'os_type', 'avatar']

    is_staff = models.BooleanField('管理员', default=False,
                                   help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('已激活', default=True,
                                    help_text='Designates whether this user should treated as active. '
                                    'Unselect this instead of deleting accounts.')
    objects = QLUserManager()

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_phone_number(self):
        return self.phone_number

    def __unicode__(self):
        if  self.name is None:
            return 'None'
        elif self.udid is None:
            return 'None'
        else:
            return '{0}-{1}'.format(self.udid, self.name)
