
import urlparse
import socket


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


class LocalhostPlugin(object):

    def pre_process_session(self, django_request, spyglass_session):
                    
        # did the user accidentally use the hostname 'localhost'?
        real_hostname = socket.gethostbyaddr(django_request.META['REMOTE_ADDR'])[0]
        real_url, corrected = replace_localhost_hostname(spyglass_session.http_url, real_hostname)

        if corrected:
            spyglass_session.http_url = real_url
            spyglass_session.autocorrected_localhost = True
        
        return corrected
            
