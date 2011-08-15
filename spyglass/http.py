
from urlparse import urlparse, urlunparse
import socket
import ssl

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import gzip


class HttpRequestor(object):
    
    def __init__(self, session, url, logger):
    
        self.session = session
        self.url = url
        self.logger = logger
        
        self.socket = None
        self.socket_file = None
        
        self.status_line = ''
        self.response_code = 0
        self.raw_headers = ''
        self.headers = {}
        
        self.raw_response = ''
    
    def start_request(self, sock):
        self.socket = sock
        
        hostname, port, raw_request = self.request_info()
        self.logger.info("Opening socket to %s:%s..." % (hostname, port))

        try:
            self.socket.connect((hostname, port))
        except socket.gaierror:
            self.logger.error("unknown host: %s" % hostname)
            self.session.http_error = 1 # TODO: make this some kind of enum
            self.session.save()
            return False
        except socket.error, msg:
            self.logger.error("socket error")
            self.logger.error(msg)
            self.session.http_error = 2 # TODO: make this some kind of enum
            self.session.save()
            return False

        self.socket.sendall(raw_request)
        return True
    
    def request_info(self):
                
        if not self.url:
            self.url = self.session.http_url
        
        parsed_url = urlparse(self.url)
        hostname = parsed_url.hostname
        path = parsed_url.path or '/'
        
        if parsed_url.scheme == 'http':
            default_port = 80
        elif parsed_url.scheme == 'https':
            if self.socket:
                self.socket = ssl.wrap_socket(self.socket)
            default_port = 443
            
        port = parsed_url.port or default_port
                
        raw_request = self.session.get_raw_request(self.url)
        
        return (hostname, port, raw_request)
    
    def read_response_headers(self):
    
        self.socket_file = self.socket.makefile()
        
        self.status_line = self.socket_file.readline()
        
        self.logger.info("Status: %s" % self.status_line.strip())
        
        self.response_code = int(self.status_line.split(' ')[1])

        receiving_headers = True
        while receiving_headers:
            raw_header = self.socket_file.readline()
            self.raw_headers += raw_header
            
            # TODO: handle multi-line headers
            
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
            self.headers[header] = value
    
    def header_value(self, key, default=None):
        return self.headers.get(key, default)
        
    def is_redirect_to_location(self):
        is_redirect = bool(300 <= self.response_code <= 399)

        location = self.header_value('location') or ''
        parsed_location = urlparse(location)
        
        if not parsed_location.netloc:
            # relative redirect
            parsed_url = urlparse(self.url)
            location = urlunparse((parsed_url.scheme, parsed_url.netloc, location, None, None, None))
            
        return is_redirect, location
    
    def read_body(self):
        transfer_coding = self.header_value('transfer-encoding', None)
        content_length = self.header_value('content-length', None)
        content_encoding = self.header_value('content-encoding', None)
        
        if transfer_coding == 'chunked':
            self.__read_chunked_body()
        elif content_length:
            try:
                length = int(content_length)
                self.__read_body_of_length(length)
            except ValueError:
                self.logger.warning("unable to parse Content-Length header: %s" % content_length)
                return
        else:
            self.logger.warning("No Content-Length or Transfer-Encoding specified.")
            self.__read_body_until_socket_closes()
            return
    
        if content_encoding == 'gzip':
            self.__decompress_gzipped_body()
    
    def __read_chunked_body(self):
        self.logger.info("Using chunked transfer-coding")
        while True:
            c = self.socket_file.readline().strip()
            
            try:
                chunk_size = int(c, 16)
            except ValueError:
                self.logger.error("reading chunk size: %s" % c)
                self.logger.error("Next Line: %s" % self.socket_file.readline())
                continue
                
            if chunk_size == 0:
                break
            else:
                data = self.socket_file.read(chunk_size)
                self.raw_response += data
                blank = self.socket_file.readline() # should be blank
                if blank.strip():
                    self.logger.warning("chunk ending not CRLF, was %s" % blank)
    
    def __read_body_of_length(self, length):
        self.logger.info("Got response with content-length %s" % length)
        data = self.socket_file.read(length)
        self.raw_response += data
        
    def __read_body_until_socket_closes(self):
        buf = 'buffer'
        while len(buf):
            buf = self.socket_file.read(128)
            self.raw_response += buf
        
    def __decompress_gzipped_body(self):
        self.logger.info("Received GZIP-compressed response")

        io = StringIO(self.raw_response)
        decompressed_body = gzip.GzipFile(fileobj=io).read()
        self.raw_response = decompressed_body

    def complete_response_text(self):
        charset = self.get_charset()
        return (self.status_line + self.raw_headers + self.raw_response).decode(charset)
    
    def get_charset(self):
        charset = 'utf8'
        content_type = self.header_value('content-type')
        if content_type and 'charset=' in content_type:
            charset = content_type[content_type.find('charset=')+8:]
        return charset        
    
    def close(self):
        self.socket_file.close()
        self.socket.close()
     
