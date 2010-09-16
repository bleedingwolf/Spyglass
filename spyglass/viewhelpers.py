
import urlparse

from django.conf import settings

from spyglass.backend import session_is_ready
from spyglass.formatters import HtmlFormatter, html_line_numbers


def mustache_context_for_session(session):
    ready = session_is_ready(session)
    html_formatter = HtmlFormatter()
    ctx = {
        'MEDIA_URL': settings.MEDIA_URL,
        'session_id': session.id,
        'complete': 'true' if ready else 'false',
    }
    
    if ready:
        if session.http_error:
            ctx['http_error'] = session.get_http_error_display()
        else:
            pretty_response = html_formatter.format(session.http_response)
            ctx['pretty_response'] = pretty_response
            ctx['response_linenos'] = html_line_numbers(pretty_response)
            ctx['elapsed_milliseconds'] = (session.time_completed - session.time_requested).microseconds / 1000.0
            ctx['redirects'] = [{'url': s.url} for s in session.httpredirect_set.all()]
    else:
        ctx['response_linenos'] = '1\n2\n3'
        ctx['pretty_response'] = '<div class="loading-placeholder" session_id="%d">Refresh the page to see results...</div>' % session.id
    return ctx


def replace_localhost_hostname(url, real_hostname):
    parsed_url = urlparse.urlparse(url)
    
    if parsed_url.hostname == 'localhost':

        if parsed_url.port:
            real_netloc = '%s:%d' % (real_hostname, parsed_url.port)
        else:
            real_netloc = real_hostname
            
        parts = list(parsed_url)
        parts[1] = real_netloc
        real_url = urlparse.urlunparse(parts)

        return real_url, True
    else:
        return url, False
