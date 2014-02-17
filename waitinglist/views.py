# coding=utf-8
# Create your views here.
from django.http import HttpResponse
import json
from waitinglist.models import Waitinglist
from waitinglist.models import Waitedlist
import time
import datetime

def checkWaitingStatus(request, number):
    print 'Number: "%s"' % number
    response_data = {}
    #Waitedlist.objects.all().delete()
    try:
        user = Waitedlist.objects.get(number = number)
    except Waitedlist.DoesNotExist:
        response_data['result'] = 0
        response_data['num'] = number
        try:
            waiting_user = Waitinglist.objects.get(number = number)
        except Waitinglist.DoesNotExist:
            try:
                waiting_user = Waitinglist.objects.get(partner = number)
            except Waitinglist.DoesNotExist:
                response_data['result'] = -1
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                user_list = list(Waitinglist.objects.values_list('id',flat=True))
                ind = user_list.index(waiting_user.id)
                response_data['behind'] = len(user_list) - 1 - ind
                response_data['before'] = ind
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            user_list = list(Waitinglist.objects.values_list('id',flat=True))
            ind = user_list.index(waiting_user.id)
            response_data['behind'] = len(user_list) - 1 - ind
            response_data['before'] = ind
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        if user.verified:
            user.delete()
            response_data['result'] = 1
            response_data['num'] = number
            # add number to offical user list
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['result'] = 2
            response_data['num'] = number
            return HttpResponse(json.dumps(response_data), content_type="application/json")


def addPartner(request, number, partner):
    # result = -1 indicates internal error, 0:parnter already in our system, 1:first time set partner, 2:changed partner, 3:can not change parnter because invited partner already in our system.
    response_data = {}
    try:
        user = Waitinglist.objects.get(number = number)
    except Waitinglist.DoesNotExist:
        #just for debug
        user = Waitinglist(number = number, partner = partner)
        #user = Waitinglist(number = number,regtime = datetime.datetime.now())
        user.save()
        response_data['result'] = -1
        response_data['partner'] = partner
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        #check whether partner is in our system already
        if Waitedlist.objects.filter(number=partner).exists():
            response_data['result'] = 0
            response_data['partner'] = partner
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if Waitinglist.objects.filter(number=partner).exists():
            response_data['result'] = 0
            response_data['partner'] = partner
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        if Waitinglist.objects.filter(partner=partner).exists():
            response_data['result'] = 0
            response_data['partner'] = partner
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        
        if user.partner == "":
            user.partner = partner
            user.save()
            response_data['result'] = 1
            response_data['partner'] = partner
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            if user.partner_verified:
                response_data['result'] = 3
                response_data['partner'] = partner
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                user.partner = partner
                user.save()
                response_data['result'] = 2
                response_data['partner'] = partner
                return HttpResponse(json.dumps(response_data), content_type="application/json")


def moveInUser(request, password, number):
    response_data = {}
    if password == "1234567890":
        offset = int(number)
        user_list = list(Waitinglist.objects.order_by('id')[:offset].values_list('id',flat = True))
        length = len(user_list)
        for i in range(0, length):
            user = Waitinglist.objects.get(id = user_list[i])
            try:
                candidate = Waitedlist.objects.get(number = user.number)
            except Waitedlist.DoesNotExist:
                candidate = Waitedlist(number = user.number, verified = True)
                candidate.save()
            #user = Waitinglist.objects.get(number = user_list[i])
            if user.partner != "":
                try:
                    partnr = Waitedlist.objects.get(number = user.partner)
                except Waitedlist.DoesNotExist:
                    partnr = Waitedlist(number = user.partner, verified = user.partner_verified)
                    partnr.save()
            user.delete()
                
                
        response_data['result'] = 1
        response_data['num'] = length
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data['result'] = 0
        return HttpResponse(json.dumps(response_data), content_type="application/json")
