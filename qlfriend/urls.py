# coding=utf-8
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from qlfriend import views

urlpatterns = patterns('',
                        # url(r'(?P<pk>[0-9]+)/$',
                        #     views.GetPicture.as_view()),    
                        url(r'(?i)add/$', views.NewFriendorUpdate.as_view()),
                        url(r'(?i)addList/$', views.NewFriendorUpdateList.as_view())
                       )

urlpatterns = format_suffix_patterns(urlpatterns)