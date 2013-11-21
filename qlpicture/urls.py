# coding=utf-8
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from qlpicture import views

urlpatterns = patterns('',
                        # url(r'(?P<pk>[0-9]+)/$',
                        #     views.GetPicture.as_view()),    
                        url(r'(?i)getPic/(?P<uuid>[a-z0-9]+)/$', views.get_picture),
                        url(r'^$',
                            views.SendPicture.as_view()),
                        url(r'^(?i)registerSessionID/$', views.RegisterSessionId.as_view()),
                        url(r'^(?i)getStartIndex/$', views.get_start_index),
                        url(r'^(?i)getMaximumIndex/(?P<session_id>[a-z0-9]+)/$', views.get_maximum_index),
                        url(r'^(?i)getPic/(?P<session_id>[a-z0-9]+)/(?P<index>[0-9]+)/$', views.get_picture_by_session_id_and_index),
                        url(r'^(?i)endSession/(?P<session_id>[a-z0-9]+)/$', views.end_session)
                       )

urlpatterns = format_suffix_patterns(urlpatterns)