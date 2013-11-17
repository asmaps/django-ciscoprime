from django.conf.urls import patterns, include, url
from .views import ApiCallView, OverviewView, RoguesView, RogueDetailView

urlpatterns = patterns('',
    url(r'^overview/$', OverviewView.as_view(), name='overview'),
    url(r'^api_call/$', ApiCallView.as_view(), name='api_call'),
    url(r'^rogues/$', RoguesView.as_view(), name='rogues'),
    url(r'^rogue/(?P<correlated>\d+)/$', RogueDetailView.as_view(), name='rogue_detail'),
)

