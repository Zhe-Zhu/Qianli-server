from django.conf.urls import patterns, include, url

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
    url(r'^users/', include('qluser.urls')),
    url(r'^pictures/', include('qlpicture.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^dialrecords/', include('dialrecords.urls')),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^notification/', include('notification.urls')),
    url(r'^friend/', include('qlfriend.urls')),
    url(r'^widget/', include('widget.urls')),
    url(r'^waitinglist/', include('waitinglist.urls'))
)
