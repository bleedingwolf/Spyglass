from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^spyglass_demo/', include('spyglass_demo.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^', include('spyglass.urls')),
    (r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': settings.MEDIA_URL + 'favicon.ico'}),
)

if settings.DEBUG:
    options = {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
    urlpatterns += patterns('django.views.static',
        (r'^static/(?P<path>.*)$', 'serve', options),
    )
