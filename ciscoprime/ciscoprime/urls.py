from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ciscoprime.views.home', name='home'),
    url(r'^main/', include('main.urls')),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'main/login.html'}, name="accounts_login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name="accounts_logout"),
    url(r'^admin/', include(admin.site.urls)),
)
