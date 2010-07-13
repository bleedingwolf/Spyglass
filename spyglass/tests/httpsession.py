
import datetime
from email.parser import HeaderParser

from django.test import TestCase
from spyglass.models import HttpSession


class HttpSessionTest(TestCase):

    def parse_request(self, request):
        status = request.splitlines()[0]
        no_status_response = '\n'.join(request.splitlines()[1:])
        
        header_parser = HeaderParser()
        
        mime_message = header_parser.parsestr(no_status_response)
        mime_headers = dict(mime_message.items())
        mime_body = mime_message.get_payload()
        
        return status, mime_headers, mime_body      

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
    
        import textwrap
    
        body = textwrap.dedent('''\
            <fake-xml>
                <key>com.bleedingwolf.PrincipalClass</key>
                <value>SomeClassName</value>
            </fake-xml>''')
        content_length = len(body)
        
        s = HttpSession(http_method='POST', http_url='http://localhost:9000/endpoint', http_body=body)
        
        expected_request = '''POST /endpoint HTTP/1.1\r\nHost: localhost\r\n''' + \
            '''Accept: */*\r\nContent-Length: %d\r\n\r\n%s''' % (content_length, body)
        
        status, mime_headers, mime_body = self.parse_request(s.get_raw_request())
               
        self.failUnlessEqual(mime_headers['Content-Length'], str(content_length))
        self.failUnlessEqual(mime_body, body)


    def test_raw_request_with_extra_headers(self):
        headers = '\r\n'.join([
            'User-Agent: Spyglass/0.1',
            'Referer: http://localhost:9000/login.jsp'
        ])
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint', http_headers=headers)
             
        status, mime_headers, mime_body = self.parse_request(s.get_raw_request())
        
        self.failUnlessEqual(mime_headers['Host'], 'localhost')
        self.failUnlessEqual(mime_headers['User-Agent'], 'Spyglass/0.1')
        self.failUnlessEqual(mime_headers['Referer'], 'http://localhost:9000/login.jsp')
        
        
    def test_raw_request_with_host_headers(self):
        headers = '\r\n'.join([
            'User-Agent: Spyglass/0.1',
            'Referer: http://localhost:9000/login.jsp',
            'Host: google.com',
        ])
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint', http_headers=headers)
        
        # this is a bit of a hack, but using the email parsing library
        # is way easier and more accurate than comparing strings
        status, mime_headers, mime_body = self.parse_request(s.get_raw_request())
        
        self.assertTrue('Host' in mime_headers)
        self.assertTrue(mime_headers['Host'] == 'google.com')


    def test_headers_method(self):
        headers = '\r\n'.join([
            'User-Agent: Spyglass/0.1',
            'User-Agent: Foobar/2.4',
            'Referer: http://localhost:9000/login.jsp',
            'Host: google.com',
        ])
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint', http_headers=headers)
        
        expected_headers = [
            ('User-Agent', 'Spyglass/0.1'),
            ('User-Agent', 'Foobar/2.4'),
            ('Referer', 'http://localhost:9000/login.jsp'),
            ('Host', 'google.com')
        ]
        
        self.failUnlessEqual(expected_headers, s.get_request_headers())


    def test_header_dicts_method(self):
        headers = '\r\n'.join([
            'User-Agent: Spyglass/0.1',
            'User-Agent: Foobar/2.4',
            'Referer: http://localhost:9000/login.jsp',
            'Host: google.com',
        ])
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint', http_headers=headers)
        
        expected_headers = [
            dict(name='User-Agent', value='Spyglass/0.1'),
            dict(name='User-Agent', value='Foobar/2.4'),
            dict(name='Referer', value='http://localhost:9000/login.jsp'),
            dict(name='Host', value='google.com')
        ]
        
        self.failUnlessEqual(expected_headers, s.header_list())


    def test_multiple_header_values(self):
        headers = '\r\n'.join([
            'Cache-Control: a',
            'Cache-Control: b',
        ])
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint', http_headers=headers)
        
        request = s.get_raw_request()
        
        self.failUnless('Cache-Control: a' in request)
        self.failUnless('Cache-Control: b' in request)
    
    
    def test_request_querystring(self):
        s = HttpSession(http_method='GET', http_url='http://localhost:9000/endpoint?q=foo+bar&q=bar&z=qux')
        querystring_params = s.querystring_params()
        
        self.failUnless(('q', 'foo bar') in querystring_params)
        self.failUnless(('q', 'bar') in querystring_params)
        self.failUnless(('z', 'qux') in querystring_params)
