from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'proxy_client.views.home', name='home'),
    url(r'^links$', 'proxy_client.views.links', name='links'),
    url(r'^tunnel/(?P<target_url>\S+)', 'proxy_client.views.tunnel', name='tunnel'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
