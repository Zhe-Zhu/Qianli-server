# coding=utf-8
# Create your views here.
"""
关于qlpicture的view函数.
目前实现的功能:
图片的发送和获取.
"""

from qlpicture.models import TalkPicture, SessionPictureInformation, SessionPicture
from qlpicture.serializers import TalkPictureSend, SessionPictureSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

import os
import re


# class SendPicture(generics.CreateAPIView):
#     queryset = TalkPicture.objects.all()
#     serializer_class = TalkPictureSend

class SendPicture(generics.UpdateAPIView):
    """根据方案1设计的SendPicture"""
    queryset = SessionPicture.objects.all()
    serializer_class = SessionPictureSerializer
    multiple_lookup_fields = ('session_id', 'index')

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.multiple_lookup_fields:
            filter[field] = self.request.DATA[field]
        return get_object_or_404(queryset, **filter)

class SendPictureReturnOnlyName(APIView):
    def post(self, request, format=None):
        serializer = TalkPictureSend(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# 改用function based view来读取图片,期间要验证读取者

class GetPicture(generics.RetrieveAPIView):
    queryset = TalkPicture.objects.all()
    serializer_class = TalkPictureSend

class RegisterSessionId(APIView):
    def post(self, request, format=None):
        try:
            session_id = request.DATA['session_id']
        except KeyError:
            return Response({"session_id":None}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            SessionPictureInformation.objects.get(session_id=session_id)
        except ObjectDoesNotExist:
            SessionPictureInformation.objects.create(session_id=session_id, maximum_index=0)
            return Response({"session_id":session_id}, status=status.HTTP_201_CREATED)
        # 清理旧的信息
        SessionPictureInformation.objects.get(session_id=session_id).delete()
        SessionPictureInformation.objects.create(session_id=session_id, maximum_index=0)
        return Response({"session_id":session_id}, status=status.HTTP_200_OK)        

@api_view(['POST'])
def get_start_index(request):
    """在发送图片前调用,从服务器返回此次发送图片的起始序号"""
    try:
        session_id = request.DATA['session_id']
        image_amount = request.DATA['image_amount']
    except KeyError:
        return Response({"message":"The parameters in request are not correct"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        current_session = SessionPictureInformation.objects.get(session_id=session_id)
    except ObjectDoesNotExist:
        return Response({"message":"The session id [%s] does not exist" % (session_id)}, status=status.HTTP_404_NOT_FOUND)
    start_index = current_session.maximum_index
    SessionPictureInformation.objects.filter(session_id=session_id).update(maximum_index=int(current_session.maximum_index)+int(image_amount)) # 用update而不是save会更高效
    return Response({"start_index":start_index}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_maximum_index(request, session_id):
    """通过session id拿到当前最大的图片序号,也就是有多少张图片-1"""
    try:
        current_session = SessionPictureInformation.objects.get(session_id=session_id)
    except ObjectDoesNotExist:
        return Response({"message":"The session id [%s] does not exist" % (session_id)}, status=status.HTTP_404_NOT_FOUND)
    return Response({"maximum_index":current_session.maximum_index}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_picture_by_session_id_and_index(request, session_id, index):
    """根据session id和图片序号获得图片"""
    directory = "picture/"
    # 验证session_id和index的有效性
    pattern = re.compile(r'^\d+$')
    if not pattern.match(index):
        return Response({'error': 'Format of index is not correct.'}, status=status.HTTP_400_BAD_REQUEST)
    # TODO 验证session_id

    # 得到图片的地址
    current_session = SessionPicture.objects.get(session_id=session_id, index=index)
    picture = str(current_session.picture)
    if os.path.isfile(picture):
        image_data = open(picture, "rb").read()
        suffix = picture.split('.')[1]
        if suffix in ["jpg", "jpeg"]:
            suffix = "jpeg"
        mimetype = ''.join(["image/", suffix])
        return HttpResponse(image_data, mimetype=mimetype)
    return Response({'error': 'No such picture'},
                            status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def end_session(request, session_id):
    """结束发送图片session时调用,清除掉所有已发送的图片的记录"""
    # try:
    #     session_id = request.DATA['session_id']
    # except KeyError:
    #     return Response("The parameters in request are not correct", status=status.HTTP_400_BAD_REQUEST)
    SessionPicture.objects.filter(session_id=session_id).delete()
    try:
        SessionPictureInformation.objects.get(session_id=session_id).delete()
    except ObjectDoesNotExist:
        pass
    return Response({"message":"Deleted."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_picture(request, uuid):
    """根据提供的uuid来获取相应的图片"""
    directory = "picture/"
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
            # image_name +=".png"
            image_name = ''.join([image_name, ".png"])
            mimetype_ext = "png"
        else:
            return Response({'error': 'No such picture'},
                            status=status.HTTP_404_NOT_FOUND)

    image_data = open(image_name, "rb").read()
    return HttpResponse(image_data, mimetype=''.join(["image/", mimetype_ext]))
