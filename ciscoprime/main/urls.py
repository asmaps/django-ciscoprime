from django.conf.urls import patterns, include, url
from .views import (
    ApiCallView, OverviewView, RoguesView, RogueDetailView, DisabledClientsView,
    FoundRogueView)

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^overview/$', OverviewView.as_view(), name='overview'),
    url(r'^api_call/$', ApiCallView.as_view(), name='api_call'),
    url(r'^rogues/$', RoguesView.as_view(), name='rogues'),
    url(r'^rogue/(?P<correlated>\d+)/$', RogueDetailView.as_view(), name='rogue_detail'),
    url(r'^disabled_clients/$', DisabledClientsView.as_view(), name='disabled_clients'),
    url(r'^found_rogue/(?P<pk>\d+)/$', FoundRogueView.as_view(), name='found_rogue'),
    
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'main/login.html'}, name="accounts_login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name="accounts_logout"),
    url(r'^admin/', include(admin.site.urls)),
)

