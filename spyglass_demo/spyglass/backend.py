
import socket
import datetime
from urlparse import urlparse
import time

from celery.decorators import task
from celery.result import AsyncResult

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import gzip

from spyglass.models import format_request, HttpRedirect, HttpSession


def session_is_ready(session):
    result = AsyncResult(session.celery_task_id)
    return result.ready()


def run_session(session):
    if session.needs_to_send_request() and not session.http_error:
        task = make_session_request.delay(session.id, session.http_url, session.follow_redirects)
        session.celery_task_id = task.task_id
        session.save()
        

@task(serializer='json')
def make_session_request(session_id, url=None, follow_redirects=False, **kwargs):
    
        session = HttpSession.objects.get(pk=session_id)
        logger = make_session_request.get_logger(**kwargs)
    
        logger.info("Starting request for session %s" % session.id)
        
        if not url:
            url = session.http_url
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        path = parsed_url.path or '/'
        
        if parsed_url.scheme == 'http':
            default_port = 80
        elif parsed_url.scheme == 'https':
            logger.warning("Request is over HTTPS! (maybe not yet implemented)")
            default_port = 443
            
        port = parsed_url.port or default_port
                
        raw_request = session.get_raw_request(url)
        
        logger.info("Making request to %s:%s..." % (hostname, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((hostname, port))
        except socket.gaierror:
            logger.error("unknown host: %s" % hostname)
            session.http_error = 1 # TODO: make this some kind of enum
            session.save()
            return False
        sock.sendall(raw_request)
        
        logger.info("Sent request, waiting for response.")
        
        receiving_headers = True
        raw_response = ''
        raw_response_headers = ''
        raw_response_body = ''
        f = sock.makefile()
        
        status = f.readline()
        raw_response += status
        
        logger.info("Status: %s" % status.strip())
        
        response_code = int(status.split(' ')[1])

        headers = {}
        while receiving_headers:
            raw_header = f.readline()
            raw_response += raw_header
            raw_response_headers += raw_header
            
            if not raw_header.strip():
                receiving_headers = False
                break
            
            try:
                header, value = raw_header.split(':', 1)
            except ValueError:
                receiving_headers = False
                break
            header = header.strip().lower()
            value = value.strip()
            headers[header] = value
             
        if 300 <= response_code <= 399 and follow_redirects:
            location = headers.get('location', None)
            if location:
                HttpRedirect(url=location, session=session).save()
                
                logger.info("Redirected to %s" % location)
                f.close()
                sock.close()
                make_session_request.delay(session.id, location, follow_redirects)
                return True
        
        transfer_coding = headers.get('transfer-encoding', None)
        content_length = headers.get('content-length', None)
        content_encoding = headers.get('content-encoding', None)
        
        if transfer_coding == 'chunked':
            while True:
                c = f.readline().strip()
                try:
                    chunk_size = int(c, 16)
                except ValueError:
                    logger.error("reading chunk size: %s" % c)
                    logger.error("Next Line: %s" % f.readline())
                    continue
                if chunk_size == 0:
                    break
                else:
                    data = f.read(chunk_size)
                    raw_response += data
                    raw_response_body += data
                    blank = f.readline() # should be blank
                    if blank.strip():
                        logger.warning("chunk ending not CRLF, was %s" % blank)
        elif content_length:
            try:
                length = int(content_length)
            except ValueError:
                logger.warning("unable to parse Content-Length header: %s" % content_length)
            data = f.read(length)
            raw_response += data
            raw_response_body += data
        
        f.close()
        sock.close()
        
        if content_encoding == 'gzip':
            logger.info("Received GZIP-compressed response")
            io = StringIO(raw_response_body)
            decompressed_body = gzip.GzipFile(fileobj=io).read()
            raw_response_body = decompressed_body
        
        session.http_response = status + raw_response_headers + raw_response_body
        session.time_completed = datetime.datetime.now()
        session.save()
        
        return True
