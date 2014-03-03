# coding=utf-8
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from waitinglist.views import checkWaitingStatus
from waitinglist.views import  addPartner
from waitinglist.views import  moveInUser
from waitinglist.views import  addToWaitedlist

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'waitinglist.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^waitingstatus/(\d+)/$', checkWaitingStatus),
                       url(r'^addpartner/(\d+)/(\d+)/$', addPartner),
                       url(r'^moveinuser/(\d+)/(\d+)/$', moveInUser),
                       url(r'^addToWaitedlist/$', addToWaitedlist),
                       )   
