from django.conf.urls import patterns, include, url
from .views import ApiCallView, OverviewView

urlpatterns = patterns('',
    url(r'^overview/$', OverviewView.as_view(), name='overview'),
    url(r'^api_call/$', ApiCallView.as_view(), name='api_call'),
)

