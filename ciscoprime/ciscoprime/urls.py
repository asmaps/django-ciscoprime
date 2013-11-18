from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/main/overview/'), name='root'),
    url(r'^main/', include('main.urls')),
)
