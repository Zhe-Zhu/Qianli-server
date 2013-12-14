# coding=utf-8
"""
Serialize beta user email

@class BetaUserEmailSerializer 
"""
from rest_framework import serializers
from widget.models import BetaUserEmail

class BetaUserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetaUserEmail