# coding=utf-8
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from qluser import views

urlpatterns = patterns('',
                       url(r'^register/$', views.RegisterBeforeVerify.as_view()),
                       url(r'^verify/$', views.RegisterAndVerify.as_view()),
                       url(r'^whoisactive/$',
                           views.QLUserWhoIsActiveByPhoneNumber.as_view()),
                       url(r'^udid/(?P<udid>[A-Za-z0-9]+)/$',
                           views.QLUserDetailsByUDID.as_view()),
                       url(r'^phone/(?P<phone_number>[0-9]+)/$',
                           views.QLUserDetailsByPhoneNumber.as_view()),
                       url(r'^email/(?P<email>\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)/$',
                           views.QLUserDetailsByEmail.as_view()),
                       url(r'^(?P<pk>[0-9]+)/$',
                           views.QLUserDetails.as_view()),
                       url(r'^update/(?P<phone_number>[0-9]+)/$', views.QLUserInformationUpdateDetail.as_view()),
                       url(r'^logout/(?P<phone_number>[0-9]+)/$', views.QLUserLogout.as_view()),
                       url(r'(?i)avatar/(?P<uuid>[a-z0-9]+)/$', views.get_avatar),
                       url(r'(?i)avatar/(?P<uuid>[a-z0-9]+_large)/$', views.get_large_avatar),
                       url(r'(?i)debug/delete/(?P<phone_number>[0-9]+)/$', views.QLUserDelete.as_view())
                       )

urlpatterns = format_suffix_patterns(urlpatterns)
