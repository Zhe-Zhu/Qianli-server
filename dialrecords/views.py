# coding = utf-8
# Create your views here.
"""
view functions about dial records.
Implemented function:
Record missed calls
"""

from dialrecords.models import MissedCalls
from dialrecords.serializers import MissedCallSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import link
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status

class RecordMissedCalls(generics.ListCreateAPIView):
    queryset = MissedCalls.objects.all()
    serializer_class = MissedCallSerializer

    def get_queryset(self):
        """
        Lookup the missed calls based on called number.
        """
        called_number = self.kwargs['called_number']
        return MissedCalls.objects.filter(called_number=called_number)

@api_view(['GET'])
def record_missedcalls_by_get(request, calling_type, called_number, calling_number):
    """
    Because of the restriction in SIP Server, trying to create a new missed call by GET method.
    example:
    /dialrecords/missedcalls/1[calling_type]/008618664565411[called_number]/008618664565411[calling_number]/
    calling_type: 1 for missed calls; 0 for reservation;
    """
    MissedCalls.objects.create(calling_type=calling_type, called_number=called_number, calling_number=calling_number)
    return Response("Create a new missed call.", status=status.HTTP_201_CREATED)

class RecordMissedCallsViewSet(viewsets.ModelViewSet):
    """
    Viewset for missedcalls.
    Include:
    list - list all records according to [called_number]
    create - create a new missed call record
    get_badge - get number of missed calls according to [called_number]
    """
    queryset = MissedCalls.objects.all()
    serializer_class = MissedCallSerializer

    def list(self, request, called_number):
        """
        Lookup the missed calls based on called number.
        """
        queryset = MissedCalls.objects.filter(called_number=called_number)
        serializer = MissedCallSerializer(queryset, many=True)
        data = serializer.data
        # remove the retrieved data
        queryset.delete()
        return Response(data)

    def destroy(self, request, called_number):
        queryset = MissedCalls.objects.filter(called_number=called_number)
        queryset.delete()
        return Response("Deleted")

    @link()
    def get_badge(self, request, called_number):
        """
        The badge number that sent by notification center.
        Get the number based on [called_number]
        """
        queryset = MissedCalls.objects.filter(called_number=called_number)
        badge_number = len(queryset)
        return Response(badge_number)