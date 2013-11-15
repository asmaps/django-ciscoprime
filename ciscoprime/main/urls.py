from django.conf.urls import patterns, include, url
from .views import ApiCallView

urlpatterns = patterns('',
    url(r'^api_call/$', ApiCallView.as_view(), name='api_call'),
)
