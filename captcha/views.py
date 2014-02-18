# coding=utf-8
# Create your views here.

from captcha.models import Captcha
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import utc

from captcha.tests import sendCaptchaForTest

import random
import datetime
import urllib2
import hashlib
import requests
import base64
import json

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 

def getCaptcha():
    # 生成验证码, 为了输入简便, 只生成4位
    # 为了中国人的习惯,最后一位只在0 1 6 8 9 中选取
    # 倒数第二位不出现4
    captcha = ''.join([str(random.randint(0,9)), str(random.randint(0,9)), random.sample(['0','1','2','3','5','6','7','8','9'],1)[0], random.sample(['0','1','6','8','9'],1)[0]])
    return captcha

def sendCaptcha(country_code, phone_number, captcha):
    # 根据不同的国家代码选择不同短信平台
    if country_code in ["0086", "+86", "86"]:
        sendCaptchaOnLuosimao(phone_number, captcha)
    elif country_code == "test":
        sendCaptchaForTest(phone_number, captcha)
    else:
        #TODO 支持国际短信平台发送
        sendCaptchaOnLuosimao(phone_number, captcha)

def sendCaptchaByVoice(phone_number, captcha):
    now = datetime.datetime.now()
    timeStamp = now.strftime("%Y%m%d%H%M%S")

    baseUrl = "https://sandboxapp.cloopen.com:8883/"
    appId = "aaf98fda44200b8f0144360d5d2909fb"
    accountSid = "ff8080813f091d74013f09f901990015"
    authToken = "8149dad772e244578a4c363cd9289f68"
    softVersion = "2013-12-26"
    verifyCode = captcha
    to = phone_number
    playTimes = "3"

    sig = hashlib.md5(accountSid+authToken+timeStamp).hexdigest().upper()
    auth = base64.b64encode(accountSid+':'+timeStamp)

    url = baseUrl+softVersion+"/Accounts/"+accountSid+"/Calls/VoiceVerify?sig="+sig

    headers = {'Accept': 'application/json', 
    'Content-Type': 'application/json;charset=utf-8',
    'content-length':'256', 'Authorization':auth}

    payload = {"appId":appId, "verifyCode":verifyCode, "playTimes":playTimes, "to":to}

    r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)


def sendCaptchaOnLuosimao(phone_number, captcha):
    resp = requests.post(("https://sms-api.luosimao.com/v1/send.json"),
    auth=("api", "key-4dabcb730d5984d391d4a6bb5405e68f"),
    data={
        "mobile": phone_number,
        "message": ''.join([captcha, "[千里验证码]"])
    },timeout=3 , verify=False);
    result =  json.loads( resp.content )

def sendCaptchaOnBayou(phone_number, captcha):
    # 发送验证码
    # 通过八优短信平台
    web_address = "http://sms.c8686.com/Api/BayouSmsApi.aspx"
    content = ''.join([captcha, "(千里验证码)"])
    # content = ''.join([captcha, "(Qianli Captcha)"])
    coding = "gb2312"
    username = "639968"
    password = "125135158"

    password_md5 = hashlib.md5()
    password_md5.update(password)
    one_encode = urllib2.quote(content.decode('utf8').encode(coding))
    # 在 urllib2 上注册 http 流处理句柄
    register_openers()
    datagen, headers = multipart_encode({"func": "sendsms",
        "username": username,
        "password": password_md5.hexdigest(),
        "smstype": 0,
        "timeflag": 0,
        "mobiles": phone_number,
        "message": one_encode
    })
    # 创建请求对象
    request = urllib2.Request(
       web_address, datagen, headers)
    # 实际执行请求并取得返回
    result = urllib2.urlopen(request)
    # 不需要检测errorcode是否为0,因为Client端并不需要接受反馈

def sendCaptchaAndUpdateDB(phone_number, country_code):
    """
    可以被外部view调用
    生成一个验证码,然后更新数据库,成功后发送该验证码到phone_number传递的手机号
    """
    try:
        phone_captcha = Captcha.objects.get(country_code=country_code,
            phone_number=phone_number)
    except ObjectDoesNotExist:
        # 如果不存在说明是第一次注册,则生成验证码并将记录写入数据库
        captcha = getCaptcha()
        Captcha.objects.create(phone_number=phone_number,
            captcha=captcha, country_code=country_code,
            generate_date=datetime.datetime.utcnow().replace(tzinfo=utc))
        phone_captcha = Captcha.objects.get(country_code=country_code,
            phone_number=phone_number)
        # 此时程序会继续运行
    # 查看日期是否过期, 设定有效期为60mins
    if phone_captcha.generate_date + datetime.timedelta(minutes=60) < datetime.datetime.utcnow().replace(tzinfo=utc):
        # 过期, 生成新的验证码, 更新数据库
        phone_captcha.captcha = getCaptcha()
        phone_captcha.generate_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        phone_captcha.save()
    # 没过期, 不修改数据库, 直接发送该验证码
    captcha = phone_captcha.captcha
    sendCaptcha(country_code, phone_number, captcha)
    return Response({"status":1}, status=status.HTTP_200_OK)
    # return Response(''.join(['Already send the Captcha to ', country_code,
    #     ' ', phone_number]))    

def isCaptchaCorrect(phone_number, country_code, captcha):
    """
    验证所输出的号码和验证码是否正确
    """
    # TODO: 记得删除, debug用
    if captcha == "9999":
        return True

    try:
        phone_captcha = Captcha.objects.get(country_code=country_code, phone_number=phone_number, captcha=captcha)
    except ObjectDoesNotExist:
        # 不存在说明验证码和号码输入错误
        return False
    # 成功验证后将其清除
    # phone_captcha.delete()
    # 不删除, 首先删除与否对验证无影响, 其次防止后续操作错误时, 验证码不会被更换
    return True

class generateCaptcha(APIView):
    """
    Check whether the captcha exists and generate it accordingly.
    """
    def post(self, request, format=None):
        phone_number = request.DATA['phone_number']
        country_code = request.DATA['country_code']
        return sendCaptchaAndUpdateDB(phone_number, country_code)
        # try:
        #     phone_captcha = Captcha.objects.get(country_code=country_code,
        #         phone_number=phone_number)
        # except ObjectDoesNotExist:
        #     # 如果不存在说明是第一次注册,则生成验证码并将记录写入数据库
        #     captcha = getCaptcha()
        #     Captcha.objects.create(phone_number=phone_number,
        #         captcha=captcha, country_code=country_code,
        #         generate_date=datetime.datetime.utcnow().replace(tzinfo=utc))
        #     phone_captcha = Captcha.objects.get(country_code=country_code,
        #         phone_number=phone_number)
        #     # 此时程序会继续运行
        # # 查看日期是否过期, 设定有效期为60mins
        # if phone_captcha.generate_date + datetime.timedelta(minutes=60) < datetime.datetime.utcnow().replace(tzinfo=utc):
        #     # 过期, 生成新的验证码, 更新数据库
        #     phone_captcha.captcha = getCaptcha()
        #     phone_captcha.generate_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        #     phone_captcha.save()
        # # 没过期, 不修改数据库, 直接发送该验证码
        # captcha = phone_captcha.captcha
        # sendCaptcha(country_code, phone_number, captcha)
        # return Response(''.join(['Already send the Captcha to ', country_code,
        #     ' ', phone_number]))

class testWhetherRecieve(APIView):
    """
    Check whether recieve something
    """
    def get(self, request, format=None):
        number = request.DATA['number']
        return Response(number)