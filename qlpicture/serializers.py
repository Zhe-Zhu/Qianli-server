# coding=utf-8
"""
序列化与qlpicture有关的HTTP信息输入和输出.
目前实现的类有:
TalkPictureSend - 序列化发送图片时要提供的信息.
"""
from rest_framework import serializers
from qlpicture.models import TalkPicture, SessionPictureInformation, SessionPicture

class TalkPictureSend(serializers.ModelSerializer):
    class Meta:
        model = TalkPicture
        read_only_fields = ('is_available',)
        
class SessionPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPicture
        read_only_fields = ('is_available',)