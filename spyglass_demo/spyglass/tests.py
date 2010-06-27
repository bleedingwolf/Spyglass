
from django.test import TestCase
import datetime

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import gzip

from spyglass.models import HttpSession
from spyglass.formatters import HttpHeadersFormatter, separate_headers_and_body
from spyglass.http import HttpRequestor


class HttpSessionTest(TestCase):

    def test_simple_unicode(self):

        s = HttpSession(http_method='GET', http_url='http://api.gowalla.com/')
        self.failUnlessEqual(unicode(s), u'GET http://api.gowalla.com/')
    
    
    def test_absolute_url(self):
    
        s = HttpSession(id=543)
        self.failUnlessEqual(s.get_absolute_url(), '/sessions/543')
        
        
    def test_raw_request_with_path(self):
        
        s = HttpSession(http_method='GET', http_url='http://api.gowalla.com/spots')
        expected_request = 'GET /spots HTTP/1.1\r\nHost: api.gowalla.com\r\nAccept: */*\r\n\r\n'
        self.failUnlessEqual(s.get_raw_request(), expected_request)
   
   
    def test_raw_request_for_index(self):
        
        s = HttpSession(http_method='GET', http_url='http://www.carfax.com')
        expected_request = 'GET / HTTP/1.1\r\nHost: www.carfax.com\r\nAccept: */*\r\n\r\n'
        self.failUnlessEqual(s.get_raw_request(), expected_request)
    
    
    def test_needs_to_send_request(self):
    
        s = HttpSession(http_method='GET', http_url='http://api.gowalla.com/')
        
        self.failUnless(s.needs_to_send_request())
        
        s.time_completed = datetime.datetime.now()
        
        self.failIf(s.needs_to_send_request())
        
    def test_raw_request_with_querystring(self):
    
        s = HttpSession(http_method='GET', http_url='http://api.flickr.com/services/rest/?method=flickr.photos.getExif')
        expected_request = 'GET /services/rest/?method=flickr.photos.getExif HTTP/1.1\r\n' + \
            'Host: api.flickr.com\r\nAccept: */*\r\n\r\n'
        self.failUnlessEqual(s.get_raw_request(), expected_request)

    def test_raw_request_with_alternate_url(self):
    
        s = HttpSession(http_method='GET', http_url='http://google.com/')
        raw_request = s.get_raw_request('http://www.google.com/')
        expected_request = 'GET / HTTP/1.1\r\n' + \
            'Host: www.google.com\r\nAccept: */*\r\n\r\n'
        
        self.failUnlessEqual(raw_request, expected_request)

    def test_raw_request_with_body(self):
    
        body = '''
            <fake-xml>
                <key>com.bleedingwolf.PrincipalClass</key>
                <value>SomeClassName</value>
            </fake-xml>
        '''
        content_length = len(body)
        
        s = HttpSession(http_method='POST', http_url='http://localhost:9000/endpoint', http_body=body)
        
        expected_request = '''POST /endpoint HTTP/1.1\r\nHost: localhost\r\n''' + \
            '''Accept: */*\r\nContent-Length: %d\r\n\r\n%s''' % (content_length, body)
                
        self.failUnlessEqual(s.get_raw_request(), expected_request)

    def test_raw_request_with_extra_headers(self):
        headers = '\r\n'.join([
            'User-Agent: Spyglass/0.1',
            'Referer: http://localhost:9000/login.jsp'
        ])
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint', http_headers=headers)
        
        expected_request = '\r\n'.join([
            'GET /endpoint HTTP/1.1',
            'Host: localhost',
            'Accept: */*',
            'User-Agent: Spyglass/0.1',
            'Referer: http://localhost:9000/login.jsp',
            '',
            '',
        ])
                
        self.failUnlessEqual(s.get_raw_request(), expected_request)

class PrettifySessionTest(TestCase):

    def test_header_formatting(self):
    
        headers = """HTTP/1.1 200 OK
Server: nginx
Date: Wed, 19 May 2010 23:26:12 GMT
Content-Type: application/json; charset=utf-8
Connection: keep-alive
Cache-Control: public, max-age=108
Expires: Wed, 19 May 2010 23:28:21 GMT
Last-Modified: Wed, 19 May 2010 23:25:21 GMT
Vary: *

"""

        formatter = HttpHeadersFormatter()
        pretty = formatter.format(headers)
        
        expected = """<span class="status">HTTP/1.1 200 OK</span>
<span class="ss">Server:</span><span class="s"> nginx</span>
<span class="ss">Date:</span><span class="s"> Wed, 19 May 2010 23:26:12 GMT</span>
<span class="ss">Content-Type:</span><span class="s"> application/json; charset=utf-8</span>
<span class="ss">Connection:</span><span class="s"> keep-alive</span>
<span class="ss">Cache-Control:</span><span class="s"> public, max-age=108</span>
<span class="ss">Expires:</span><span class="s"> Wed, 19 May 2010 23:28:21 GMT</span>
<span class="ss">Last-Modified:</span><span class="s"> Wed, 19 May 2010 23:25:21 GMT</span>
<span class="ss">Vary:</span><span class="s"> *</span>""".replace('\n', '\r\n')

        self.failUnlessEqual(pretty, expected)
        
        
    def test_separate_headers_and_body(self):
    
        raw_response = """HTTP/1.1 200 OK
Server: nginx
Date: Wed, 19 May 2010 23:26:12 GMT

My content goes here."""

        headers, body = separate_headers_and_body(raw_response)
        
        expected_headers = """HTTP/1.1 200 OK
Server: nginx
Date: Wed, 19 May 2010 23:26:12 GMT""".replace('\n', '\r\n')

        expected_body = "My content goes here."
        
        self.failUnlessEqual(headers, expected_headers)
        self.failUnlessEqual(body, expected_body)

    
    def test_separate_headers_and_empty_body(self):
    
        raw_request = """GET /users/flair/5616.json HTTP/1.1
Host: stackoverflow.com
Accept: */*

"""
        headers, body = separate_headers_and_body(raw_request)
        
        expected_headers = """GET /users/flair/5616.json HTTP/1.1
Host: stackoverflow.com
Accept: */*""".replace('\n', '\r\n')

        expected_body = ""
        
        self.failUnlessEqual(headers, expected_headers)
        self.failUnlessEqual(body, expected_body)


class MockSocket(object):

    def __init__(self, response_data=''):
        self.hostname = ''
        self.port = 0
    
        self.fileobj = StringIO(response_data)
        self.recv_data = ''
    
    def connect(self, param):
        self.hostname, self.port = param
    
    def sendall(self, data):
        self.recv_data += data
    
    def makefile(self):
        return self.fileobj
    
    def close(self):
        pass

class MockLogger(object):

    def __init__(self):
        self.messages = []
    
    def recordMessage(self, msg):
        self.messages.append(msg)
    
    debug = recordMessage
    info = recordMessage
    warning = recordMessage
    error = recordMessage

class HttpRequestorTest(TestCase):
    
    def setUp(self):
        session = HttpSession(http_method='GET', http_url='http://localhost:7010/console')
        logger = MockLogger()
        self.requestor = HttpRequestor(session, None, logger)
    
    def test_parsing_simple_response_headers(self):
        sock = MockSocket(response_data='HTTP/1.1 200 OK\r\nServer: nginx\r\nDate: Sat, 26 Jun 2010 04:03:37 GMT\r\nContent-Type: application/json; charset=utf-8\r\n\r\n')

        self.requestor.start_request(sock)
        self.requestor.read_response_headers()
        
        self.failUnlessEqual(self.requestor.header_value('server'), 'nginx')
        self.failUnlessEqual(self.requestor.header_value('content-type'), 'application/json; charset=utf-8')
        self.failUnlessEqual(self.requestor.header_value('date'), 'Sat, 26 Jun 2010 04:03:37 GMT')


    def test_parsing_redirect_response(self):
        sock = MockSocket(response_data='HTTP/1.0 307 Temporary Redirect\r\nServer: nginx\r\nDate: Sat, 26 Jun 2010 04:03:37 GMT\r\nLocation: http://news.ycombinator.com/\r\n\r\n')

        self.requestor.start_request(sock)
        self.requestor.read_response_headers()
        
        is_redirect, location = self.requestor.is_redirect_to_location()
        
        self.assertTrue(is_redirect)
        self.failUnlessEqual(location, 'http://news.ycombinator.com/')

    def test_reading_response_with_content_length(self):
        sock = MockSocket(response_data='HTTP/1.0 200 OK\r\nServer: nginx\r\nDate: Sat, 26 Jun 2010 04:03:37 GMT\r\nContent-length: 4\r\n\r\nGoodBad')

        self.requestor.start_request(sock)
        self.requestor.read_response_headers()
        self.requestor.read_body()
        
        response = self.requestor.raw_response
        
        self.failUnlessEqual(response, 'Good')

    def test_reading_response_with_not_enough_content(self):
        sock = MockSocket(response_data='HTTP/1.0 200 OK\r\nServer: nginx\r\nDate: Sat, 26 Jun 2010 04:03:37 GMT\r\nContent-length: 40\r\n\r\nNotQuiteEnough')

        self.requestor.start_request(sock)
        self.requestor.read_response_headers()
        self.requestor.read_body()
        
        response = self.requestor.raw_response
        
        self.failUnlessEqual(response, 'NotQuiteEnough')
        
    def test_reading_response_with_no_content_length(self):
        sock = MockSocket(response_data='HTTP/1.0 200 OK\r\nServer: nginx\r\nDate: Sat, 26 Jun 2010 04:03:37 GMT\r\n\r\nThis content has no specified length.')

        self.requestor.start_request(sock)
        self.requestor.read_response_headers()
        self.requestor.read_body()
        
        response = self.requestor.raw_response
        
        self.failUnlessEqual(response, 'This content has no specified length.')
    
    # TODO: more tests
    #   - test chunked response body
    #   - test gzipped response data
    #   - test multi-line headers
        