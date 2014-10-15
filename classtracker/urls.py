from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tardy_tracker.views.base', name='base'),
    url(r'^view_course/$', 'tardy_tracker.views.view_course', name='view_course'),
    url(r'^home/$', 'tardy_tracker.views.home', name='home'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^teacher/$', 'tardy_tracker.views.teacher_home', name='teacher_home'),
)
