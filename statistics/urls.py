# coding=utf-8
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from statistics.views import getUserStas

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'waitinglist.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^users/(\d+)/(\d+)/$', getUserStas),
                       )   
