# coding=utf-8
# Create your views here.

import smtplib
import re
from email.mime.text import MIMEText
from email.header import Header

from widget.models import BetaUserEmail
from widget.serializers import BetaUserEmailSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

def sendMailBy163(beta_user_email):
    sender = 'paladin88@163.com'
    receiver = 'theashstudio@gmail.com'
    subject = '申请加入千里内测'
    smtpserver = 'smtp.163.com'
    username = 'paladin88'
    password = 'zz88261025'

    msg = MIMEText(beta_user_email,'plain','utf-8')#中文需参数‘utf-8’，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')

    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com')
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()

def validateEmail(email):
    if len(email) > 5:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

class StoreBetaUserEmail(generics.ListCreateAPIView):
    queryset = BetaUserEmail.objects.all()
    serializer_class = BetaUserEmailSerializer

    def post(self, request, format=None):
        try:
            email = request.DATA['email']
        except KeyError:
            return Response({"msg":"no email"}, status=status.HTTP_400_BAD_REQUEST)

        if validateEmail(email) == 0:
            return Response({"msg":"not email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            beta_user = BetaUserEmail.objects.get(email=email)
        except BetaUserEmail.DoesNotExist:
            BetaUserEmail.objects.create(email=email)
            sendMailBy163(email)
            return Response({"msg":"OK"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg":"OK"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def store_email_by_get(request):
    try:
        email = request.GET.get('email')
    except KeyError:
        return Response({"msg":"no email"}, status=status.HTTP_400_BAD_REQUEST)

    if validateEmail(email) == 0:
        return Response({"msg":"not email"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        beta_user = BetaUserEmail.objects.get(email=email)
    except BetaUserEmail.DoesNotExist:
        BetaUserEmail.objects.create(email=email)
        sendMailBy163(email)
        return Response({"msg":"OK"}, status=status.HTTP_200_OK)
    else:
        return Response({"msg":"OK"}, status=status.HTTP_200_OK)    