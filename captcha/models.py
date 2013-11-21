# coding=utf-8
from django.db import models

# Create your models here.

class Captcha(models.Model):
    """
    存储用户的手机号和验证码,用以验证该手机号是否正确
    还需要存储时间,用以验证时间是否过期
    """
    phone_number = models.CharField('手机号码', max_length=20, db_index=True)
    country_code = models.CharField('国家代码', max_length=10, db_index=True)
    captcha = models.CharField('验证码', max_length=10)
    generate_date = models.DateTimeField('生成验证码的时间')

    def __unicode__(self):
        return self.phone_number

