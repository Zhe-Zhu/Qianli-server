# coding=utf-8
"""
Serialize dial records.
Implemented classes:
QLFriendSerializer - serialize friend list
"""
from rest_framework import serializers
from qlfriend.models import QLFriend

class QLFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = QLFriend