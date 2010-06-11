
import socket
import datetime
from urlparse import urlparse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import gzip

from spyglass.models import format_request, HttpRedirect

def run_session(session, url=None, follow_redirects=False):

    if session.needs_to_send_request():
    
        print " [INFO] Starting request for session %s" % session.id
    
        if not url:
            url = session.http_url
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        path = parsed_url.path or '/'
        
        if parsed_url.scheme == 'http':
            default_port = 80
        elif parsed_url.scheme == 'https':
            print " [WARN] Request is over HTTPS! (may not be implemented)"
            default_port = 443
            
        port = parsed_url.port or default_port
                
        raw_request = session.get_raw_request()
        
        print " [INFO] Making request to %s:%s..." % (hostname, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        sock.sendall(raw_request)
        
        print " [INFO] Sent request, waiting for response."
        
        receiving_headers = True
        raw_response = ''
        raw_response_headers = ''
        raw_response_body = ''
        f = sock.makefile()
        
        status = f.readline()
        raw_response += status
        
        print " [INFO] Status: %s" % status.strip()
        
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
                
                print " [INFO] Redirected to %s" % location
                f.close()
                sock.close()
                run_session(session, location, follow_redirects)
                return
        
        transfer_coding = headers.get('transfer-encoding', None)
        content_length = headers.get('content-length', None)
        content_encoding = headers.get('content-encoding', None)
        
        if transfer_coding == 'chunked':
            while True:
                c = f.readline().strip()
                try:
                    chunk_size = int(c, 16)
                except ValueError:
                    print "[ERROR] reading chunk size: %s" % c
                    print "[ERROR] Next Line: %s" % f.readline()
                    continue
                if chunk_size == 0:
                    break
                else:
                    data = f.read(chunk_size)
                    raw_response += data
                    raw_response_body += data
                    blank = f.readline() # should be blank
                    if blank.strip():
                        print " [WARN] chunk ending not CRLF, was %s" % blank
        elif content_length:
            try:
                length = int(content_length)
            except ValueError:
                print " [WARN] unable to parse Content-Length header: %s" % content_length
            data = f.read(length)
            raw_response += data
            raw_response_body += data
        
        f.close()
        sock.close()
        
        if content_encoding == 'gzip':
            print " [INFO] Received GZIP-compressed response"
            io = StringIO(raw_response_body)
            decompressed_body = gzip.GzipFile(fileobj=io).read()
            raw_response_body = decompressed_body
        
        session.http_response = raw_response_headers + raw_response_body
        session.time_completed = datetime.datetime.now()
        session.save()
