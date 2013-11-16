from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/main/overview/'), name='root'),
    url(r'^main/', include('main.urls')),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'main/login.html'}, name="accounts_login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name="accounts_logout"),
    url(r'^admin/', include(admin.site.urls)),
)
