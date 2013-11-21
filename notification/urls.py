from django.conf.urls import patterns, include, url
from notification import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
                      url(r'^hello/$', views.hello),
                      url(r'^gettoken/$',views.received_token),
                      url(r'^send/$', views.SendNotification.as_view()),
                      url(r'^(?i)sendByGet/(?P<notification_type>[0-9])/(?P<phone_number_receiver>[0-9]+)/(?P<phone_number_sender>[0-9]+)/$', views.send_notification_by_get)
)
