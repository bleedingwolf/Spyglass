
from django.test import TestCase
import datetime

from spyglass.models import HttpSession
from spyglass.formatters import HttpHeadersFormatter, separate_headers_and_body

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
        