# coding=utf-8
# Create your views here.

from qluser.models import QLUser, QLUserInformationUpdate
from qluser.serializers import QLUserSerializer, QLUserSerializerAfterRegister, QLUserInformationUpdateSerializer
from waitinglist.models import Waitinglist, Waitedlist, IsWaiting
from captcha.views import sendCaptchaAndUpdateDB, isCaptchaCorrect
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from mysite import settings
from django.http import HttpResponse, HttpResponseNotFound

import MySQLdb
import hashlib
import xml.dom.minidom
import os
import re

def register_sip_server(obj):
    db = MySQLdb.connect(host="localhost",
                         user="openser",
                         passwd="openserrw",
                         db="openser")
    cur = db.cursor()
    realm = "qianli"
    m = hashlib.md5(obj.udid + ':' + realm + ':' + obj.password)
    ha1 = m.hexdigest()
    m = hashlib.md5(
        obj.udid + '@112.124.36.134' + ':' + realm + ':' + obj.password)
    ha1b = m.hexdigest()
    # 删除掉旧的记录
    number_row = cur.execute("DELETE FROM subscriber WHERE username="+"'"+obj.phone_number+"'")
    number_row = cur.execute("INSERT INTO subscriber (username, domain, password, ha1, ha1b, email_address) VALUES (" +
                             "'" + obj.phone_number + "','" + "112.124.36.134" +"','" + obj.password + "','" + ha1 + "','" + ha1b + "','" + obj.email + "')" + "ON DUPLICATE KEY UPDATE domain=VALUES(domain), password=VALUES(password), ha1=VALUES(ha1), ha1b=VALUES(ha1b), email_address=VALUES(email_address)")
    # TODO:需要检测是否执行成功
    if number_row != 1:
        pass  # TODO: do something here
    db.commit()
    cur.close()
    db.close()


class Register(generics.CreateAPIView):
    queryset = QLUser.objects.all()
    serializer_class = QLUserSerializer

    def post_save(self, obj, created=False):
        """
        将记录插入已有的数据库中,让SIP服务器可以接受用户登录.
        """
        db = MySQLdb.connect(host="localhost",
                             user="openser",
                             passwd="openserrw",
                             db="openser")
        cur = db.cursor()
        realm = "qianli"
        m = hashlib.md5(obj.udid + ':' + realm + ':' + obj.password)
        ha1 = m.hexdigest()
        m = hashlib.md5(
            obj.udid + '@112.124.36.134' + ':' + realm + ':' + obj.password)
        ha1b = m.hexdigest()
        number_row = cur.execute("INSERT INTO subscriber (username, domain, password, ha1, ha1b, email_address) VALUES (" +
                                 "'" + obj.udid + "','112.124.36.134','" + obj.password + "','" + ha1 + "','" + ha1b + "','" + obj.email + "')")
        # TODO:需要检测是否执行成功
        if number_row != 1:
            pass  # TODO: do something here
        db.commit()
        cur.close()
        db.close()

class RegisterBeforeVerify(generics.CreateAPIView):
    """
    如果phone_number和udid和原有记录一致,则不需要重新建立记录和发送验证码,直接跳过验证界面
    如果不一致,则进入验证码发送和验证阶段
    具体操作流程为:
    1. 手机发起注册请求, 附带参数需包含udid和phone_number
    2. check udid 和 phone_number是否和原纪录一致
    3. if not 则生成验证码并将该记录插入验证码临时数据表并将验证码发送
    4. 等用户在手机输入验证码后, 手机发起验证请求, 附带参数要包含所有用户信息以及所输入的验证码
    5. 先验证输入的验证码是否和插入的一致(通过phone_number检索)
    6. if yes 则将原有和该号码和该udid相关的所有记录删除(为简单起见,目前udid和号码一一对应,如果要兼容其他设备,需要将电话号码唯一属性取消,而且需要有选择地删除和该号码相关记录)
    7. 将用户数据插入用户表,注册完成
    """
    queryset = QLUser.objects.all()
    serializer_class = QLUserSerializer

    def post(self, request, format=None):
        try:
            phone_number = request.DATA['phone_number']
            udid = request.DATA['udid']
        except KeyError:
            return Response({"status": -1}, status=status.HTTP_400_BAD_REQUEST)
        try:
            old_user = QLUser.objects.get(phone_number=phone_number, udid=udid)
        except ObjectDoesNotExist:
            """
            检查waitinglist和waitedlist
            """
            if Waitinglist.objects.filter(number=phone_number).exists():
                return Response({"status":3}, status=status.HTTP_200_OK)
            if Waitinglist.objects.filter(partner=phone_number).exists():
                if Waitinglist.objects.filter(partner=phone_number)[0].partner_verified == True:
                    return Response({"status":4}, status=status.HTTP_200_OK)
            if Waitedlist.objects.filter(number=phone_number).exists():
                if Waitedlist.objects.filter(number=phone_number)[0].verified==True:
                    return Response({"status":5}, status=status.HTTP_200_OK)
            """
            开始发送验证码并将其插入数据表
            """
            country_code = phone_number[0:4]
            pure_phone_number = phone_number[4:]
            return sendCaptchaAndUpdateDB(pure_phone_number, country_code)
        # 不需要发送验证码, 直接通过验证, 并将is_active标志位置为真
        old_user.is_active = True
        old_user.save()
        register_sip_server(old_user)
        return Response({"status":2}, status=status.HTTP_200_OK)

        #     serializer = QLUserSerializer(data=request.DATA)
        #     if serializer.is_valid():
        #         obj = serializer.save()
        #         self.register_sip_server(obj)
        #         return Response({"status":1}, status=status.HTTP_201_CREATED)
        #     else:
        #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # if udid == old_user.udid:
        #     return Response({"status":2}, status=status.HTTP_200_OK)
        # else:
        #     old_user.delete()
        #     serializer = QLUserSerializer(data=request.DATA)
        #     if serializer.is_valid():
        #         obj = serializer.save()
        #         self.register_sip_server(obj)
        #         return Response({"status":1}, status=status.HTTP_201_CREATED)
        #     else:
        #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAndVerify(APIView):
    """
    负责实现验证验证码是否正确和完成用户注册的工作
    {
    4. 等用户在手机输入验证码后, 手机发起验证请求, 附带参数要包含所有用户信息以及所输入的验证码
    5. 先验证输入的验证码是否和插入的一致(通过phone_number检索)
    6. if yes 则将原有和该号码和该udid相关的所有记录删除(为简单起见,目前udid和号码一一对应,如果要兼容其他设备,需要将电话号码唯一属性取消,而且需要有选择地删除和该号码相关记录)
    7. 将用户数据插入用户表,注册完成
    }
    """
    def post(self, request, format=None):
        try:
            phone_number = request.DATA['phone_number']
            captcha = request.DATA['captcha']
            udid = request.DATA['udid']
        except KeyError:
            return Response({"status": 0}, status=status.HTTP_400_BAD_REQUEST)
        country_code = phone_number[0:4]
        pure_phone_number = phone_number[4:]
        if isCaptchaCorrect(pure_phone_number, country_code, captcha):
            # 查看是否在waited list或waiting list的partner里
            if Waitinglist.objects.filter(partner=phone_number).exists():
                waiting_partner =  Waitinglist.objects.filter(partner=phone_number)[0]
                waiting_partner.partner_udid = udid
                waiting_partner.partner_verified = True
                waiting_partner.save()
                return Response({"status":4}, status=status.HTTP_200_OK)
            if Waitedlist.objects.filter(number=phone_number).exists():
                waited = Waitedlist.objects.filter(number=phone_number)[0]
                waited.udid = udid
                waited.verified = True
                waited.save()
                return Response({"status":3}, status=status.HTTP_200_OK)
            if IsWaiting.objects.get(id=1).is_waiting:
                try:
                    Waitinglist.objects.get(number=phone_number).delete()
                except ObjectDoesNotExist:
                    pass
                Waitinglist.objects.create(number=phone_number, udid=udid)
                return Response({"status":2}, status=status.HTTP_200_OK)
            else:
                # 验证成功将用户记录插入数据库
                try:
                    # 清理旧记录
                    QLUser.objects.get(phone_number=phone_number).delete()
                except ObjectDoesNotExist:
                    pass
                try:
                    # 必须分开清理,否则如果出现异常则不执行下面一条了
                    QLUser.objects.get(udid=udid).delete()
                except ObjectDoesNotExist:
                    pass
                serializer = QLUserSerializer(data=request.DATA)
                if serializer.is_valid():
                    obj = serializer.save()
                    # 将旧记录删除并将记录插入已有的数据库中,让SIP服务器可以接受用户登录.
                    # self.register_sip_server(obj)
                    register_sip_server(obj)
                    # 将该用户插入信息更新记录表
                    self.insert_into_user_information_update(obj)
                    return Response({"status":1}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":0}, status=status.HTTP_200_OK)
        
    def insert_into_user_information_update(self, obj):
        old_user_information = None
        try:
            old_user_information = QLUserInformationUpdate.objects.get(phone_number=obj.phone_number)
        except ObjectDoesNotExist:
            pass
        if old_user_information is not None:
            old_user_information.delete()
        QLUserInformationUpdate.objects.create(phone_number=obj.phone_number, update_time=0)

    # def register_sip_server(self, obj):
    #     db = MySQLdb.connect(host="localhost",
    #                          user="openser",
    #                          passwd="openserrw",
    #                          db="openser")
    #     cur = db.cursor()
    #     realm = "qianli"
    #     m = hashlib.md5(obj.udid + ':' + realm + ':' + obj.password)
    #     ha1 = m.hexdigest()
    #     m = hashlib.md5(
    #         obj.udid + '@112.124.36.134' + ':' + realm + ':' + obj.password)
    #     ha1b = m.hexdigest()
    #     # 删除掉旧的记录
    #     number_row = cur.execute("DELETE FROM subscriber WHERE username="+"'"+obj.phone_number+"'")
    #     number_row = cur.execute("INSERT INTO subscriber (username, domain, password, ha1, ha1b, email_address) VALUES (" +
    #                              "'" + obj.phone_number + "','" + "112.124.36.134" +"','" + obj.password + "','" + ha1 + "','" + ha1b + "','" + obj.email + "')" + "ON DUPLICATE KEY UPDATE domain=VALUES(domain), password=VALUES(password), ha1=VALUES(ha1), ha1b=VALUES(ha1b), email_address=VALUES(email_address)")
    #     # TODO:需要检测是否执行成功
    #     if number_row != 1:
    #         pass  # TODO: do something here
    #     db.commit()
    #     cur.close()
    #     db.close()

    # def post_save(self, obj, created=False):
    #     # 将记录插入已有的数据库中,让SIP服务器可以接受用户登录.
    #     self.register_sip_server(obj)
    #     # 将该用户插入信息更新记录表
    #     self.insert_into_user_information_update(obj)

class QLUserDetails(generics.RetrieveUpdateAPIView):
    queryset = QLUser.objects.all()
    serializer_class = QLUserSerializer

# 不允许修改,修改应该另外重开一个接口


class QLUserDetailsByUDID(generics.RetrieveAPIView):
    queryset = QLUser.objects.all()
    serializer_class = QLUserSerializerAfterRegister
    lookup_field = 'udid'

class QLUserDetailsByPhoneNumber(generics.RetrieveUpdateAPIView):
    queryset = QLUser.objects.all()
    serializer_class = QLUserSerializerAfterRegister
    lookup_field = 'phone_number'

    def insert_into_user_information_update(self, obj):
        old_user_information = None
        try:
            old_user_information = QLUserInformationUpdate.objects.get(phone_number=obj.phone_number)
        except ObjectDoesNotExist:
            pass
        if old_user_information is not None:
            old_user_information.delete()
        QLUserInformationUpdate.objects.create(phone_number=obj.phone_number, update_time=0)

    def pre_save(self, obj, created=False):
        """
        删除旧头像
        """
        try:
            old_information = QLUser.objects.get(phone_number=obj.phone_number)
        except ObjectDoesNotExist:
            return
        # 删除旧头像 只有在有所更新的时候才删除
        if obj.avatar != old_information.avatar and bool(old_information.avatar):
            old_information.avatar.delete()
        if obj.large_avatar != old_information.large_avatar and bool(old_information.large_avatar):
            old_information.large_avatar.delete()

    def post_save(self, obj, created=False):
        """
        更新标志位, 便于通知用户重新拿取名字和头像数据
        """
        try:
            user_information = QLUserInformationUpdate.objects.get(phone_number=obj.phone_number)
        except ObjectDoesNotExist:
            self.insert_into_user_information_update(obj)
            user_information = QLUserInformationUpdate.objects.get(phone_number=obj.phone_number)
        user_information.update_time = user_information.update_time + 1
        if user_information.update_time>3000:
            user_information.update_time = 0
        user_information.save()

class QLUserDetailsByEmail(generics.RetrieveAPIView):
    queryset = QLUser.objects.all()
    serializer_class = QLUserSerializerAfterRegister
    lookup_field = 'email'

class QLUserInformationUpdateDetail(generics.RetrieveAPIView):
    """查看该用户是否更新信息"""
    queryset = QLUserInformationUpdate.objects.all()
    serializer_class = QLUserInformationUpdateSerializer
    lookup_field = 'phone_number'

class QLUserLogout(APIView):
    """
    将用户注销, 需要进行的操作有:
    将isActive标志位置为0, 使得不会在其他用户的联系人中出现
    update information, user information和sip server的信息均不删除, 因为重新注册时需要使用, 如果更换了手机则相应的记录也会在注册中删除并更新
    """
    def delete(self, request, phone_number, format=None):
        try:
            old_user = QLUser.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            return Response({"message": "Cannot find such user with the number-%s" % (phone_number)}, status=status.HTTP_400_BAD_REQUEST)
        old_user.is_active = False
        old_user.delete()
        #old_user.save()
        return Response({"message": "already log out for user with number-%s" % (phone_number)}, status=status.HTTP_200_OK)

class QLUserDelete(APIView):
    """
    将用户删除, 需要进行的操作有:
    将isActive标志位置为0, 使得不会在其他用户的联系人中出现
    update information, user information和sip server的信息均不删除, 因为重新注册时需要使用, 如果更换了手机则相应的记录也会在注册中删除并更新
    """
    def delete(self, request, phone_number, format=None):
        try:
            old_user = QLUser.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            return Response({"message": "Cannot find such user with the number-%s" % (phone_number)}, status=status.HTTP_400_BAD_REQUEST)
        old_user.delete()
        return Response({"message": "already delete user with number-%s" % (phone_number)}, status=status.HTTP_200_OK)

class QLUserWhoIsActiveByPhoneNumber(APIView):
    """
    Check which phone number is activated in Qianli
    Cannot use non-ascii encoded stiring(Chinese) here o.w. it will cause [UnicodeDecodeError]
    """
    def post(self, request, format=None):
        phone_number_list = request.DATA
        # 这里已经对request的数据自动parse了,所以后面不需要做JSONParser
        # return Response(data["a"])
        # return Response(data=='["a"]')
        # stream = StringIO.StringIO(data)
        # # return Response(stream)
        # # phone_number_list = JSONParser().parse(stream)
        # # phone_number_list = simplejson.load(stream)
        # # return Response(stream.read())
        # return Response("[u'a']"==stream.read())
        return_phone_number = []
        for phone_number in phone_number_list:
            if self.isActive(phone_number):
                return_phone_number.append(phone_number)
        return_phone_number = list(set(return_phone_number))
        return Response(return_phone_number)

    def isActive(self, phone_number):
        """
        Check if the number is active. If so return true.
        """
        try:
            QLUser.objects.get(phone_number=phone_number, is_active=True)
        except ObjectDoesNotExist:
            return False
        return True

@api_view(['GET'])
def get_avatar(request, uuid):
    """根据提供的uuid来获取相应的图片"""
    directory = os.path.join(settings.MEDIA_ROOT, 'avatar/')
    # 验证uuid有效性,必须是32个字母或数字的组合
    pattern = re.compile(r'^[a-z0-9]{32}$')
    if not pattern.match(uuid):
        return Response({'error': 'Format of uuid is not correct'},
                        status=status.HTTP_400_BAD_REQUEST)
    # 验证文件是否存在
    image_name = directory + uuid
    if os.path.isfile(image_name + ".jpg"):
        # image_name += ".jpg"
        # 采用join方法,效率更高,不需要新建字符串对象
        image_name = ''.join([image_name, ".jpg"])
        mimetype_ext = "jpeg"
    elif os.path.isfile(image_name + ".jpeg"):
        image_name = ''.join([image_name, ".jpeg"])
        mimetype_ext = "jpeg"
    else:
        if os.path.isfile(image_name + ".png"):
            image_name = ''.join([image_name, ".png"])
            mimetype_ext = "png"
        elif os.path.isfile(image_name):
            mimetype_ext = 'png'
        else:
            return Response({'error': 'No such picture ' + image_name},
                            status=status.HTTP_404_NOT_FOUND)

    image_data = open(image_name, "rb").read()
    return HttpResponse(image_data, mimetype=''.join(["image/", mimetype_ext]))

@api_view(['GET'])
def get_large_avatar(request, uuid):
    """根据提供的uuid来获取相应的图片"""
    directory = os.path.join(settings.MEDIA_ROOT, 'avatar/')
    # 验证uuid有效性,必须是32个字母或数字的组合
    pattern = re.compile(r'^[a-z0-9]{32}_large$')
    if not pattern.match(uuid):
        return Response({'error': 'Format of uuid is not correct'},
                        status=status.HTTP_400_BAD_REQUEST)
    # 验证文件是否存在
    image_name = directory + uuid
    if os.path.isfile(image_name + ".jpg"):
        # image_name += ".jpg"
        # 采用join方法,效率更高,不需要新建字符串对象
        image_name = ''.join([image_name, ".jpg"])
        mimetype_ext = "jpeg"
    elif os.path.isfile(image_name + ".jpeg"):
        image_name = ''.join([image_name, ".jpeg"])
        mimetype_ext = "jpeg"
    else:
        if os.path.isfile(image_name + ".png"):
            image_name = ''.join([image_name, ".png"])
            mimetype_ext = "png"
        elif os.path.isfile(image_name):
            mimetype_ext = 'png'
        else:
            return Response({'error': 'No such picture ' + image_name},
                            status=status.HTTP_404_NOT_FOUND)

    image_data = open(image_name, "rb").read()
    return HttpResponse(image_data, mimetype=''.join(["image/", mimetype_ext]))