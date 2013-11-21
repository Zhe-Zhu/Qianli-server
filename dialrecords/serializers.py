# coding=utf-8
"""
Serialize dial records.
Implemented classes:
MissedCallSerializer - serialize the information that records the missed calls
"""
from rest_framework import serializers
from dialrecords.models import MissedCalls

class MissedCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissedCalls