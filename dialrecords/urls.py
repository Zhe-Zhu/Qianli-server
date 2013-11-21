# coding=utf-8
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from dialrecords import views
from dialrecords.views import RecordMissedCallsViewSet

missedcalls_create = RecordMissedCallsViewSet.as_view({
    'post': 'create'
    })

missedcalls_list = RecordMissedCallsViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'delete': 'destroy'
    })
missedcalls_badge = RecordMissedCallsViewSet.as_view({
    'get': 'get_badge'
    })

urlpatterns = patterns('',
                        # url(r'(?P<pk>[0-9]+)/$',
                        #     views.GetPicture.as_view()),    
                        # url(r'missedcalls/(?P<called_number>[0-9]+)/$', views.RecordMissedCalls.as_view())
                        url(r'missedcalls/$', missedcalls_create),
                        url(r'missedcalls/(?P<called_number>[0-9]+)/$', missedcalls_list),
                        url(r'missedcalls/(?P<called_number>[0-9]+)/badge/$', missedcalls_badge),
                        url(r'missedcalls/(?P<calling_type>[0-9])/(?P<called_number>[0-9]+)/(?P<calling_number>[0-9]+)/$', views.record_missedcalls_by_get)
                       )

urlpatterns = format_suffix_patterns(urlpatterns)