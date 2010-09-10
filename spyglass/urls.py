from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'spyglass.views.homepage'),
    (r'^create/$', 'spyglass.views.create_session'),
    (r'^sessions/(\d+)$', 'spyglass.views.session_detail'),
    (r'^sessions/(\d+)/is_complete\.json$', 'spyglass.views.session_completed_jsonp'),
    (r'^sessions/(\d+)/resend$', 'spyglass.views.session_resend'),
    
    url(r'^sessions/$', 'django.views.generic.simple.redirect_to', {'url': '/sessions/mine'}, name='session_list'),
    (r'^sessions/mine', 'spyglass.views.session_list_mine'),
    (r'^sessions/all', 'spyglass.views.session_list_all'),
)