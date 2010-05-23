from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^create$', 'spyglass.views.create_session'),
    (r'^session/(\d+)$', 'spyglass.views.session_detail'),
    (r'^session/(\d+)/resend$', 'spyglass.views.session_resend'),
)