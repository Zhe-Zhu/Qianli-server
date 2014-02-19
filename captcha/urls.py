# coding=utf-8
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from captcha import views

urlpatterns = patterns('',
                        # url(r'(?P<pk>[0-9]+)/$',
                        #     views.GetPicture.as_view()),    
                        url(r'sendcaptcha/$', views.generateCaptcha.as_view()),
                        url(r'testWhetherRecieve/$', views.testWhetherRecieve.as_view())，
                        url(r'sendcaptchabyvoice/$', views.sendCaptchaByVoice.as_view())
                       )

urlpatterns = format_suffix_patterns(urlpatterns)