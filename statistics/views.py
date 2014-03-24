# coding=utf-8
# Create your views here.
from django.http import HttpResponse
import json
from qluser.models import QLUser, QLUserInformationUpdate
from statistics.models import Stats
import time
import datetime
import pytz
from pytz import timezone
import MySQLdb
import hashlib
import requests
from django.core.exceptions import ObjectDoesNotExist
import threading
import thread
from django.core.mail import send_mail
from django.core.mail import EmailMessage


def getUserStas(request, num_activeuser, num_callingSession):
    
    date = datetime.datetime.now()
    stats = Stats(number_active_user = num_activeuser, number_sesiion = num_callingSession, year = date.year, month = date.month, day = date.day, hour = date.hour, sent = False)
    stats.save()
    
    statsList = list(Stats.objects.filter(sent=False).values_list('id',flat = True))
    if len(statsList) > 23:
        #num_qluser = QLUser.objects.count()
        message = ''
        for i in range(0, len(statsList)):
            entry = Stats.objects.get(id = statsList[i])
            
            string = "online users: %d,  active session: %d   %d-%d-%d-%d" % (entry.number_active_user, entry.number_sesiion, entry.year, entry.month, entry.day, entry.hour)
            message = ' \n'.join([message, string])
            entry.sent = True
            entry.save()
        #cainholic@gmail.com, cxw1987@gmail.com
        msg = EmailMessage('statistics from qinali server', message, to=['lt2010cuhk@gmail.com'])
        msg.send()

        msg1 = EmailMessage('statistics from qinali server', message, to=['cxw1987@gmail.com'])
        msg1.send()
    
        msg2 = EmailMessage('statistics from qinali server', message, to=['cainholic@gmail.com'])
        msg2.send()


    response_data = {}
    response_data['retCode'] = 0
    return HttpResponse(json.dumps(response_data), content_type="application/json")


