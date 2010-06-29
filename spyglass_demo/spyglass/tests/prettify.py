
from django.test import TestCase
from spyglass.formatters import HttpHeadersFormatter, separate_headers_and_body, prettify_xml


class PrettifySessionTest(TestCase):

    def test_header_formatting(self):
    
        headers = '\r\n'.join([
        	'HTTP/1.1 200 OK',
			'Server: nginx',
			'Date: Wed, 19 May 2010 23:26:12 GMT',
			'Content-Type: application/json; charset=utf-8',
			'Connection: keep-alive',
			'Cache-Control: public, max-age=108',
			'Expires: Wed, 19 May 2010 23:28:21 GMT',
			'Last-Modified: Wed, 19 May 2010 23:25:21 GMT',
			'Vary: *',
			'',
			''
		])

        formatter = HttpHeadersFormatter()
        pretty = formatter.format(headers)
        
        expected = '\r\n'.join([
			'<span class="status">HTTP/1.1 200 OK</span>',
			'<span class="ss">Server:</span><span class="s"> nginx</span>',
			'<span class="ss">Date:</span><span class="s"> Wed, 19 May 2010 23:26:12 GMT</span>',
			'<span class="ss">Content-Type:</span><span class="s"> application/json; charset=utf-8</span>',
			'<span class="ss">Connection:</span><span class="s"> keep-alive</span>',
			'<span class="ss">Cache-Control:</span><span class="s"> public, max-age=108</span>',
			'<span class="ss">Expires:</span><span class="s"> Wed, 19 May 2010 23:28:21 GMT</span>',
			'<span class="ss">Last-Modified:</span><span class="s"> Wed, 19 May 2010 23:25:21 GMT</span>',
			'<span class="ss">Vary:</span><span class="s"> *</span>'
		])

        self.failUnlessEqual(pretty, expected)
        
        
    def test_separate_headers_and_body(self):
    
        raw_response = '\r\n'.join([
        	'HTTP/1.1 200 OK',
			'Server: nginx',
			'Date: Wed, 19 May 2010 23:26:12 GMT',
			'',
			'My content goes here.'
		])

        headers, body = separate_headers_and_body(raw_response)
        
        expected_headers = '\r\n'.join([
        	'HTTP/1.1 200 OK',
			'Server: nginx',
			'Date: Wed, 19 May 2010 23:26:12 GMT'
		])

        expected_body = "My content goes here."
        
        self.failUnlessEqual(headers, expected_headers)
        self.failUnlessEqual(body, expected_body)

    
    def test_separate_headers_and_empty_body(self):
    
        raw_request = '\r\n'.join([
        	'GET /users/flair/5616.json HTTP/1.1',
			'Host: stackoverflow.com',
			'Accept: */*',
			'',
			''
		])

        headers, body = separate_headers_and_body(raw_request)
        
        expected_headers = '\r\n'.join([
        	'GET /users/flair/5616.json HTTP/1.1',
			'Host: stackoverflow.com',
			'Accept: */*'
		])

        expected_body = ""
        
        self.failUnlessEqual(headers, expected_headers)
        self.failUnlessEqual(body, expected_body)

    
class PrettifyXMLTest(TestCase):

    def test_really_simple_xml(self):
        xml = '<xml></xml>'
        pretty_xml = prettify_xml(xml)
        
        self.assertEquals('<xml>\n</xml>', pretty_xml)
    
    def test_intermediate_xml(self):
        xml = '<root><child><sub-child>Foo</sub-child><sub-child>Bar</sub-child></child></root>'
        pretty_xml = prettify_xml(xml)
        expected_xml = '\n'.join([
            '<root>',
            '  <child>',
            '    <sub-child>Foo</sub-child>',
            '    <sub-child>Bar</sub-child>',
            '  </child>',
            '</root>'
        ])
        
        self.assertEquals(pretty_xml, expected_xml)
    
    def test_ignores_xml_prefix(self):
        xml = '<?xml version="1.0"?><root><child><sub-child>Foo</sub-child><sub-child>Bar</sub-child></child></root>'
        pretty_xml = prettify_xml(xml)
        expected_xml = '\n'.join([
            '<?xml version="1.0"?>',
            '<root>',
            '  <child>',
            '    <sub-child>Foo</sub-child>',
            '    <sub-child>Bar</sub-child>',
            '  </child>',
            '</root>'
        ])
        
        self.assertEquals(pretty_xml, expected_xml)
            