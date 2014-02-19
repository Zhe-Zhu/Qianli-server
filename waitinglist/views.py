# coding=utf-8
# Create your views here.
from django.http import HttpResponse
import json
from waitinglist.models import Waitinglist
from waitinglist.models import Waitedlist
from waitinglist.models import IsWaiting
from qluser.models import QLUser, QLUserInformationUpdate
import time
import datetime
import MySQLdb
import hashlib
from django.core.exceptions import ObjectDoesNotExist

def insert_into_user_information_update(phone_number):
    old_user_information = None
    try:
        old_user_information = QLUserInformationUpdate.objects.get(phone_number=phone_number)
    except ObjectDoesNotExist:
        pass
    if old_user_information is not None:
        old_user_information.delete()
    QLUserInformationUpdate.objects.create(phone_number=phone_number, update_time=0)


def register_sip_server(udid, phone_number):
    db = MySQLdb.connect(host="localhost",
                         user="openser",
                         passwd="openserrw",
                         db="openser")
    cur = db.cursor()
    realm = "qianli"
    password = phone_number
    email = ""
    m = hashlib.md5(udid + ':' + realm + ':' + password)
    ha1 = m.hexdigest()
    m = hashlib.md5(
        udid + '@112.124.36.134' + ':' + realm + ':' + password)
    ha1b = m.hexdigest()
    # 删除掉旧的记录
    number_row = cur.execute("DELETE FROM subscriber WHERE username="+"'"+phone_number+"'")
    number_row = cur.execute("INSERT INTO subscriber (username, domain, password, ha1, ha1b, email_address) VALUES (" +
                             "'" + phone_number + "','" + "112.124.36.134" +"','" + password + "','" + ha1 + "','" + ha1b + "','" + email + "')" + "ON DUPLICATE KEY UPDATE domain=VALUES(domain), password=VALUES(password), ha1=VALUES(ha1), ha1b=VALUES(ha1b), email_address=VALUES(email_address)")
    # TODO:需要检测是否执行成功
    if number_row != 1:
        pass  # TODO: do something here
    db.commit()
    cur.close()
    db.close()


def checkWaitingStatus(request, number):
    print 'Number: "%s"' % number
    response_data = {}
    
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
                response_data['partner'] = waiting_user.number;
                response_data['verified'] = True;
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            user_list = list(Waitinglist.objects.values_list('id',flat=True))
            ind = user_list.index(waiting_user.id)
            response_data['behind'] = len(user_list) - 1 - ind
            response_data['before'] = ind
            response_data['partner'] = waiting_user.partner;
            response_data['verified'] = waiting_user.partner_verified;
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        if user.verified:
            udid = user.udid
            user.delete()
            response_data['result'] = 1
            response_data['num'] = number
            response_data['behind'] = Waitinglist.objects.count()
            #TODO: add number to official user list
            # 验证成功将用户记录插入数据库
            try:
                # 清理旧记录
                QLUser.objects.get(phone_number=number).delete()
            except ObjectDoesNotExist:
                pass
            try:
                # 必须分开清理,否则如果出现异常则不执行下面一条了
                QLUser.objects.get(udid=udid).delete()
            except ObjectDoesNotExist:
                pass
            QLUser.objects.create(udid=udid, phone_number=number, password=number, email="")
            register_sip_server(udid, number)
            insert_into_user_information_update(number)         
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
        if QLUser.objects.filter(phone_number=partner).exists():
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
                # can not change the partner if your partner is already in our system
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
                candidate = Waitedlist(number = user.number, udid = user.udid, verified = True)
                candidate.save()
            #user = Waitinglist.objects.get(number = user_list[i])
            if user.partner != "":
                try:
                    partnr = Waitedlist.objects.get(number = user.partner)
                except Waitedlist.DoesNotExist:
                    partnr = Waitedlist(number = user.partner, udid = user.partner_udid, verified = user.partner_verified)
                    partnr.save()
            user.delete()
                
                
        response_data['result'] = 1
        response_data['num'] = length
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        if password == "0987654321":
            offset = int(number)
            if offset == 1:
                isWaiting = IsWaiting.objects.get(id = 1);
                isWaiting.is_waiting = True;
                isWaiting.save()
            else:
                isWaiting = IsWaiting.objects.get(id = 1);
                isWaiting.is_waiting = False;
                isWaiting.save()
                
            response_data['result'] = 1
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data['result'] = 0
            return HttpResponse(json.dumps(response_data), content_type="application/json")
