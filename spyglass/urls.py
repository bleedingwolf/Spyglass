from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'spyglass.views.homepage'),
    (r'^create/$', 'spyglass.views.create_session'),
    (r'^sessions/(\d+)$', 'spyglass.views.session_detail'),
    (r'^sessions/(\d+)/is_complete\.json$', 'spyglass.views.session_completed_jsonp'),
    (r'^sessions/(\d+)/resend$', 'spyglass.views.session_resend'),
    (r'^sessions/', 'spyglass.views.session_list'),
)