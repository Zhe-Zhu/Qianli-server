# coding=utf-8
# Create your views here.
from django.http import Http404, HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from notification.models import LastFeedback
from notification.models import UserInfo
from dialrecords.models import MissedCalls
from qlfriend.models import QLFriend
from qluser.models import QLUser

#from apns import APNs, Payload, PayloadAlert
#from pyapns import configure, provision, notify, feedback

from pprint import pprint
import threading
import time
import datetime
import json
import os
import logging

# @csrf_exempt
# def hello_old_with_apns(request):
#     apns = APNs(use_sandbox=True, cert_file='/usr/share/nginx/www/qianli/Certificates.pem', key_file='/usr/share/nginx/www/qianli/Certificates.pem')
    
#     # Send a notification
#     number = request.body.replace(" ", "")
#     number = number.replace("<","")
#     number = number.replace(">","")
#     try:
#         user =  UserInfo.objects.get(name = number)
#     except UserInfo.DoesNotExist:
#         print 'not exists!'
#         return HttpResponse("The user doesn't exist")
#     else:
#         token_hex = user.token
    
#     # token_hex = '3498f0627ff5abe8fc202e13ff54aa74cef5f99a9aa0888ceee8ae9b8bc45dde'
#     print 'Token Data: "%s"' % token_hex
#     alert = PayloadAlert("Hello world!", action_loc_key="Click me")
#     payload = Payload(alert=alert, sound="default", badge=1)
#     # payload = Payload(alert="Hello World!", sound="default", badge=1)
#     apns.gateway_server.send_notification(token_hex, payload)
#     tmr = TimerClass()
#     tmr.start()
#     html = "<html>send notification</html>"
#     return HttpResponse(html)

def run_twisted():
    if len(os.popen("netstat -nltp | grep 7077").readlines()) < 1 or len(os.popen("pgrep twistd").readlines()) < 1:
        os.system("twistd -r epoll web --class=pyapns.server.APNSServer --port=7077")


def send_notification(token, aps):
    """
    向目标手机发送通知:
    token - 目标手机的token
    aps - 通知的payload,包括显示数字和内容等
    """
    run_twisted()
    configure({'HOST': 'http://localhost:7077/'})
    # provision('lg2013', open('/usr/share/nginx/www/qianli/apns-dev.pem').read(), 'sandbox')
    # notify('lg2013', token, aps)    
    # provision('com.ashstudio.qianli', open('/usr/share/nginx/www/qianli/development.pem').read(), 'sandbox')
    # provision('com.ashstudio.qianli', open('/usr/share/nginx/www/qianli/apns-dev.pem').read(), 'sandbox')
    # 有且只能provision一次!!!如果有相同的app id, 第二次将视为无效
    provision('com.ashstudio.qianli', open('/usr/share/nginx/www/qianli/apns-pro.pem').read(), 'production')
    provision('com.development.qianli', open('/usr/share/nginx/www/qianli/apns-dev.pem').read(), 'sandbox')
    notify('com.ashstudio.qianli', token, aps)
    notify('com.development.qianli', token, aps)
    # provision('com.ashstudio.qianliAdhocDistribution', open('/usr/share/nginx/www/qianli/apns-pro.pem').read(), 'production')
    # notify('com.ashstudio.qianliAdhocDistribution', token, aps)

    logger = logging.getLogger(__name__)
    logger.debug("send notification LG")
    try:
       feedbacktime =  LastFeedback.objects.get(name = 'APNS')
    except LastFeedback.DoesNotExist:
       feedbacktime = LastFeedback(name = 'APNS', lastfeedback = datetime.datetime.now())
       feedbacktime.save()

    da=datetime.datetime.now()
    daydelta=da.day-feedbacktime.lastfeedback.day
    hourdelta=da.hour-feedbacktime.lastfeedback.hour
    secondsdelta = daydelta * 86400 + hourdelta * 3600
    if secondsdelta>86400:
       logger = logging.getLogger(__name__)
       logger.debug("execute feedback service")
       feedbacktime.lastfeedback = datetime.datetime.now()
       feedbacktime.save()
       feedback('com.ashstudio.qianli', async=True, callback=got_feedback)

def got_feedback(tuples):
   logger = logging.getLogger(__name__)
   logger.debug("get reply from feedback service")
   for tup in tuples:
       try:
         user =  UserInfo.objects.get(token = tup[1])
       except UserInfo.DoesNotExist:
         logger = logging.getLogger(__name__)
         logger.debug('not find the user with this token in feedback')
       else:
         logger = logging.getLogger(__name__)
         logger.debug('decide whether should delete this token or not')
         lasttime = user.lastregtime
         if lasttime < tup[0]:
            user.delete()
            logger = logging.getLogger(__name__)
            logger.debug('deleteed token in feedback')

def try_to_send_notification(notification_type, phone_number_sender, phone_number_receiver):
    """
    尝试向目标手机发送通知:
    """
    # 获取badget number
    records = MissedCalls.objects.filter(called_number=phone_number_receiver)
    badge_number = len(records)
    # 获取token
    try:
        user = UserInfo.objects.get(name=phone_number_receiver)
    except UserInfo.DoesNotExist:
        return Response({"message": "Not found such user."}, status=status.HTTP_404_NOT_FOUND)
    token = user.token

    # 获取用户名字
    # 优先使用用户通讯录中的名字,如果没有则使用用户自己设定的名字,如果还是没有则使用用户的号码
    try:
        friend = QLFriend.objects.get(user_number=phone_number_receiver, friend_number=phone_number_sender)
    except QLFriend.DoesNotExist:
        try:
            sender_profile = QLUser.objects.get(phone_number=phone_number_sender)
        except QLUser.DoesNotExist:
            sender_name = None
        else:
            sender_name = sender_profile.name
        if sender_name is None:
            sender_name = phone_number_sender
    else:
        sender_name = friend.friend_name

    if notification_type == '0':
        # 通知类型为电话
        aps = {'aps': {
                        'sound': 'ringtone.mp3',
                        'badge': badge_number,
                        'alert': {'loc-key':'PUSHCALLING',
                                  'loc-args':[sender_name],
                                  'action-loc-key':'PUSHACTIONKEY'}}
            }   
    elif notification_type == '1':
        # 通知类型为预约
        # 将该预约记录下来
        MissedCalls.objects.create(called_number=phone_number_receiver, calling_number=phone_number_sender, calling_type='0')

        aps = {'aps': {
                        'sound': 'default',
                        'badge': badge_number+1,
                        'alert':{ 'loc-key':'APPOINTMENT',
                                 'loc-args':[sender_name],
                                 'action-loc-key':'APPOINTMENTACTIONKEY'}}
            }
    elif notification_type == '2':
        # 通知类型为未接来电
        # 将该记录存下来
        MissedCalls.objects.create(called_number=phone_number_receiver, calling_number=phone_number_sender, calling_type='1')
        # 时间记录下来
        # current_day = time.strftime('%d',time.localtime(time.time()))
        # current_time = time.strftime('%H:%M',time.localtime(time.time()))
        aps = {'aps': {
                        'sound': 'default',
                        'badge': badge_number+1,
                        'alert': {
                                    'loc-key':'MISSEDCALL',
                                    'loc-args':[sender_name],
                                    'action-loc-key':'MISSEDCALLACTIONKEY'
                        }
        }
        }

    # 发送通知
    send_notification(token, aps)
    #tmr = TimerClass()
    #tmr.start()
    return Response({"message": "send notification."}, status=status.HTTP_200_OK)

class SendNotification(APIView):
    """
    发送notification给被呼叫方手机, 接收三个参数:\n
    type - 0电话 1预约\n
    phone_number_sender - 呼叫方手机\n
    phone_number_receiver - 被叫方手机\n
    """
    def post(self, request, format=None):
        try:
            notification_type = request.DATA['type']
            phone_number_sender = request.DATA['phone_number_sender']
            phone_number_receiver = request.DATA['phone_number_receiver']
        except KeyError:
            return Response({"message": "KeyError. Check the parameters please."}, status=status.HTTP_400_BAD_REQUEST)
        return try_to_send_notification(notification_type, phone_number_sender, phone_number_receiver)

@api_view(['GET'])
def send_notification_by_get(request, notification_type, phone_number_receiver, phone_number_sender):
    """
    Because of the restriction in SIP Server, trying to create a new missed call by GET method.
    example:
    /notification/sendbyget/1[type]/008618664565411[phone_number_receiver]/008618664565411[phone_number_sender]/
    """
    return try_to_send_notification(notification_type, phone_number_sender, phone_number_receiver)

@csrf_exempt
def hello(request):
    # run twisted if it is not running
    run_twisted()
    # get the token
    number = request.body.replace(" ", "")
    number = number.replace("<","")
    number = number.replace(">","")
    try:
        user =  UserInfo.objects.get(name = number)
    except UserInfo.DoesNotExist:
        print 'not exists!'
        return HttpResponse("The user doesn't exist")
    else:
        token_hex = user.token    

    aps = {'aps': {
                'sound': 'default',
                'badge': 1,
                'message': 'Hello from Qianli :)'}
    }
    configure({'HOST': 'http://localhost:7077/'})
    provision('lg2013', open('/usr/share/nginx/www/qianli/apns-dev.pem').read(), 'sandbox')
    notify('lg2013', token_hex, aps)
    tmr = TimerClass()
    tmr.start()
    html = "<html>send notification</html>"
    return HttpResponse(html)

@csrf_exempt
def received_token(request):
    receivedStr = request.body.replace(" ", "")
    token_hex,temp,number = receivedStr.partition("*")
    token_hex = token_hex.replace("<","")
    token_hex = token_hex.replace(">","")
    print 'Token Body Data: "%s"' % token_hex
    print 'Number: "%s"' % number
    
    try:
       user =  UserInfo.objects.get(name = number)
    except UserInfo.DoesNotExist:
         user = UserInfo(name = number, token = token_hex, lastregtime = datetime.datetime.now())
         user.save()
         print 'new item'
    else:
         user.token = token_hex
         user.lastregtime = datetime.datetime.now()
         user.save()
         print 'update item'
    
    to_json = {
        "Succeed": "YES",
        "Token": request.body
    }
    return HttpResponse(simplejson.dumps(to_json), mimetype="application/json")

