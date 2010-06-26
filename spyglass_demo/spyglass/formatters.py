
from django.template.defaultfilters import force_escape

import json
from xml.dom.minidom import parseString

from pygments import highlight
from pygments.formatters import HtmlFormatter as PygmentsHtmlFormatter
from pygments.lexers import guess_lexer, JavascriptLexer


class HttpHeadersFormatter(object):

    def format(self, headers):
        safe_headers = force_escape(headers)
        split_headers = safe_headers.splitlines()
        
        status = '<span class="status">%s</span>' % split_headers[0]
        pretty_headers = []
        for header in split_headers[1:]:
            if not header:
                continue
            try:
                h, v = header.split(':', 1)
            except ValueError:
                continue
            pretty_h = '<span class="ss">%s:</span><span class="s">%s</span>' % (h, v)
            pretty_headers.append(pretty_h)
        
        result = '\r\n'.join([status] + pretty_headers)
        
        return result


class HtmlFormatter(object):

    def format(self, data):
        headers, body = separate_headers_and_body(data)
        
        header_formatter = HttpHeadersFormatter()
        pretty_headers = header_formatter.format(headers)
        
        pretty_body = self._format_body(body)
        
        separator = '\r\n'
        if pretty_body.strip():
            separator = '\r\n\r\n'
        return pretty_headers + separator + pretty_body
    
    def _format_body(self, response_body):
        if not response_body:
            return ''
        
        try:
            pretty_response_body = self.__format_xml(response_body)
        except Exception, ex:
            try:
                pretty_response_body = self.__format_json(response_body)
            except ValueError, ex2:
                pretty_response_body = response_body
    
        lexer = guess_lexer(pretty_response_body)
        formatter = PygmentsHtmlFormatter(nowrap=True)
        pretty_response_body = highlight(pretty_response_body, lexer, formatter)
            
        return pretty_response_body
    
    def __format_json(self, text):
        tmp = json.loads(text)
        return json.dumps(tmp, indent=4)
    
    def __format_xml(self, text):
        dom_document = parseString(text)
        return dom_document.toprettyxml(indent='  ')


def separate_headers_and_body(raw_text):

    split_text = raw_text.splitlines()
    header_list = []

    for h in split_text:
        if not h.strip():
            break
        header_list.append(h)
    
    headers = '\r\n'.join(header_list)
    body = '\r\n'.join(split_text[len(header_list)+1:])
    
    return headers, body


def html_line_numbers(raw_text):
    split_data = raw_text.splitlines()
    return '\r\n'.join([str(i+1) for i in xrange(len(split_data))])
