# coding=utf-8
from rest_framework import serializers
from qluser.models import QLUser, QLUserInformationUpdate

import re

class QLUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = QLUser
        fields = ('udid', 'password', 'name', 'phone_number', 'email', 'os_type', 'avatar', 'large_avatar')
        read_only_fields = ('is_staff', 'is_active',)

    def validate(self, attrs):
        """验证手机号码和邮箱必须输入一个"""
        if not (attrs['phone_number'] or attrs['email']):
            raise serializers.ValidationError('手机号和邮箱必须要提供一个')
        return attrs     

    def validate_phone_number(self, attrs, source):
        """验证手机号是否正确"""
        value = attrs[source]
        pattern = re.compile(r'[0-9]+')
        match = pattern.match(value)
        if not match:
            raise serializers.ValidationError('Wrong format in phone number')
        return attrs

class QLUserSerializerAfterRegister(serializers.ModelSerializer):
    """在完成用户注册后使用,用以限制某些信息不被读取和修改"""
    class Meta:
        model = QLUser
        fields = ('udid', 'name', 'phone_number', 'email', 'os_type', 'avatar', 'large_avatar')
        read_only_fields = ('udid', 'phone_number',) #一定要加',' 否则会出错

class QLUserInformationUpdateSerializer(serializers.ModelSerializer):
    """供用户读取其好友是否更新了信息"""
    class Meta:
        model = QLUserInformationUpdate