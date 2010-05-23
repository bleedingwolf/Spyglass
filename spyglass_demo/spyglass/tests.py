
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
        self.failUnlessEqual(s.get_absolute_url(), '/session/543')
        
        
    def test_raw_request_with_path(self):
        
        s = HttpSession(http_method='GET', http_url='http://api.gowalla.com/spots')
        expected_request = 'GET /spots HTTP/1.1\r\nHost: api.gowalla.com\r\nAccept: */*\r\n\r\n'
        self.failUnlessEqual(s.get_raw_request(), expected_request)
   
   
    def test_raw_request_for_index(self):
        
        s = HttpSession(http_method='GET', http_url='http://www.carfax.com/')
        expected_request = 'GET / HTTP/1.1\r\nHost: www.carfax.com\r\nAccept: */*\r\n\r\n'
        self.failUnlessEqual(s.get_raw_request(), expected_request)
    
    
    def test_needs_to_send_request(self):
    
        s = HttpSession(http_method='GET', http_url='http://api.gowalla.com/')
        
        self.failUnless(s.needs_to_send_request())
        
        s.time_completed = datetime.datetime.now()
        
        self.failIf(s.needs_to_send_request())


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
<span class="header">Server:</span><span class="header-value"> nginx</span>
<span class="header">Date:</span><span class="header-value"> Wed, 19 May 2010 23:26:12 GMT</span>
<span class="header">Content-Type:</span><span class="header-value"> application/json; charset=utf-8</span>
<span class="header">Connection:</span><span class="header-value"> keep-alive</span>
<span class="header">Cache-Control:</span><span class="header-value"> public, max-age=108</span>
<span class="header">Expires:</span><span class="header-value"> Wed, 19 May 2010 23:28:21 GMT</span>
<span class="header">Last-Modified:</span><span class="header-value"> Wed, 19 May 2010 23:25:21 GMT</span>
<span class="header">Vary:</span><span class="header-value"> *</span>""".replace('\n', '\r\n')

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
        