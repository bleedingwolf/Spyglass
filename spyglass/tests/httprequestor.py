
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.test import TestCase
from spyglass.models import HttpSession
from spyglass.http import HttpRequestor


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
    