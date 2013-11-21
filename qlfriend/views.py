# coding=utf-8
# Create your views here.

from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from qlfriend.models import QLFriend
from qlfriend.serializers import QLFriendSerializer

class NewFriendorUpdate(APIView):
    """
    加入或更新一个已有好友的名字\n
    example:\n
    {\n
    "user_number": "008618664565400",\n
    "friend_number": "008618664565400",\n
    "friend_name": "ZZ"\n
    }
    """
    def put(self, request, format=None):
        try:
            user_number = request.DATA['user_number']
            friend_number = request.DATA['friend_number']
            friend_name = request.DATA['friend_name']
        except KeyError:
            return Response({"message": "KeyError. Check the parameters please."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            friend = QLFriend.objects.get(user_number=user_number, friend_number=friend_number)
        except QLFriend.DoesNotExist:
            QLFriend.objects.create(user_number=user_number, friend_number=friend_number, friend_name=friend_name)
            return Response({"message": "Add a new friend."}, status=status.HTTP_201_CREATED)
        friend.friend_name = friend_name
        friend.save()
        return Response({"message": "update a friend name."}, status=status.HTTP_200_OK)

class NewFriendorUpdateList(APIView):
    """
    批量加入或更新一个已有好友的名字
    example:
    {\n
    "user_number": "008618664565400",\n
    "friends": [\n
        {\n
            "phone_number": "111",\n
            "name": "111"\n
        },\n
        {\n
            "phone_number": "111",\n
            "name": "111"\n
        },\n
        {\n
            "phone_number": "111",\n
            "name": "111"\n
        }\n
    ]\n
    }
    """
    def put(self, request, format=None):
        try:
            user_number = request.DATA['user_number']
            friends = request.DATA['friends']
        except KeyError:
            return Response({"message": "KeyError. Check the parameters please."}, status=status.HTTP_400_BAD_REQUEST)

        for user_friends in friends:
            friend_number = user_friends['phone_number']
            friend_name = user_friends['name']
            try:
                friend = QLFriend.objects.get(user_number=user_number, friend_number=friend_number)
            except QLFriend.DoesNotExist:
                QLFriend.objects.create(user_number=user_number, friend_number=friend_number, friend_name=friend_name)
            else:
                friend.friend_name = friend_name
                friend.save()
        return Response({"message": "update a few friends name."}, status=status.HTTP_200_OK)