# coding=utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from captcha.models import Captcha

import urllib2
import datetime

def sendCaptchaForTest(phone_number, captcha):
    # 在本地创建一个验证码文件来存储发送的验证码用于测试
    captcha_output = open("/Users/user/Documents/Workspace/Python/djcode/mysite/resourceForTest/captcha", 'w')
    captcha_output.write(captcha)

def getCaptchaForTest():
    # 读取本地所创建的文件中的验证码
    captcha_output = open("/Users/user/Documents/Workspace/Python/djcode/mysite/resourceForTest/captcha")
    return captcha_output.readline()

def sendRequestToServer(country_code, phone_number):
    web_address = "http://127.0.0.1:8000/captcha/sendcaptcha/"
    register_openers()
    datagen, headers = multipart_encode({
        "country_code": country_code,
        "phone_number": phone_number
        })
    request = urllib2.Request(web_address, datagen, headers)
    result = urllib2.urlopen(request)

class CaptchaTest(TestCase):
    def test_first_time_send_captcha(self):
        """
        最基本的发送验证码的功能, 当用户第一次输入手机号时会遇到
        """
        url = "/captcha/sendcaptcha/"
        country_code = "test"
        phone_number = "18664565400"
        self.client.post(url, {"country_code": country_code,
            "phone_number": phone_number})
        phone_captcha = Captcha.objects.get(country_code=country_code, phone_number=phone_number)
        self.assertEqual(phone_captcha.captcha, getCaptchaForTest())
        
    def test_resend_captcha_no_expiration(self):
        """
        当用户点击重传按钮时,验证码并没过期
        """
        url = "/captcha/sendcaptcha/"
        country_code = "test"
        phone_number = "18664565400"
        self.client.post(url, {"country_code": country_code,
            "phone_number": phone_number})
        captcha = Captcha.objects.get(country_code=country_code, phone_number=phone_number).captcha
        self.client.post(url, {"country_code": country_code,
            "phone_number": phone_number})
        captcha_resend = Captcha.objects.get(country_code=country_code, phone_number=phone_number).captcha
        self.assertEqual(captcha, captcha_resend)
        self.assertEqual(captcha, getCaptchaForTest())

    def test_resend_captcha_expiration(self):
        """
        当用户点击重传按钮, 验证码过期了.
        注意: 当重新生成验证码的时候,有可能会正好生成和原来一样的验证码,所以有很小的
        概率这个测试会失败
        """
        url = "/captcha/sendcaptcha/"
        country_code = "test"
        phone_number = "18664565400"
        self.client.post(url, {"country_code": country_code,
            "phone_number": phone_number})
        phone_captcha = Captcha.objects.get(country_code=country_code, phone_number=phone_number)
        captcha_sent = getCaptchaForTest()
        phone_captcha.generate_date = phone_captcha.generate_date - datetime.timedelta(minutes=61)
        phone_captcha.save()
        self.client.post(url, {"country_code": country_code,
            "phone_number": phone_number})
        self.assertNotEqual(captcha_sent, getCaptchaForTest())
