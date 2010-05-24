
import socket
import datetime
from urlparse import urlparse

from spyglass.models import format_request, HttpRedirect

def run_session(session, url=None, follow_redirects=False):

    if session.needs_to_send_request():
    
        if not url:
            url = session.http_url
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        path = parsed_url.path or '/'
        
        raw_request = format_request(session.http_method, hostname, path)
        
        print "[INFO] Making request to %s..." % hostname
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, 80))
        sock.sendall(raw_request)
        
        receiving_headers = True
        raw_response = ''
        f = sock.makefile()
        
        status = f.readline()
        raw_response += status
        
        print "[INFO] Status: %s" % status.strip()
        
        response_code = int(status.split(' ')[1])

        headers = {}
        while receiving_headers:
            raw_header = f.readline()
            raw_response += raw_header
            
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
                print "[TODO] log redirect"
                HttpRedirect(url=location, session=session).save()
                
                print "[INFO] Redirected to %s" % location
                f.close()
                sock.close()
                run_session(session, location, follow_redirects)
                return
        
        transfer_coding = headers.get('transfer-encoding', None)
        content_length = headers.get('content-length', None)
        
        if transfer_coding == 'chunked':
            while True:
                c = f.readline().strip()
                try:
                    chunk_size = int(c, 16)
                except ValueError:
                    print "Error reading chunk size: %s" % c
                    print "Next Line: %s" % f.readline()
                    continue
                if chunk_size == 0:
                    break
                else:
                    raw_response += f.read(chunk_size)
                    blank = f.readline() # should be blank
                    if blank.strip():
                        print "WARN: chunk ending not CRLF, was %s" % blank
        elif content_length:
            try:
                length = int(content_length)
            except ValueError:
                print "WARN: unable to parse Content-Length header: %s" % content_length
            raw_response += f.read(length)
        
        f.close()
        sock.close()
        
        print "[INFO] Received %d bytes from host." % len(raw_response)
        
        session.http_response = raw_response
        session.time_completed = datetime.datetime.now()
        session.save()
