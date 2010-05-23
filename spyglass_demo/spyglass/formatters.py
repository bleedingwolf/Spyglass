
from django.template.defaultfilters import force_escape

import json
from pygments import highlight
from pygments.formatters import HtmlFormatter as PygmentsHtmlFormatter
from pygments.lexers import get_lexer_for_mimetype, JavascriptLexer


class HttpHeadersFormatter(object):

    def format(self, headers):
        safe_headers = force_escape(headers)
        split_headers = safe_headers.splitlines()
        
        status = '<span class="status">%s</span>' % split_headers[0]
        pretty_headers = []
        for header in split_headers[1:]:
            if not header:
                continue
            h, v = header.split(':', 1)
            pretty_h = '<span class="header">%s:</span><span class="header-value">%s</span>' % (h, v)
            pretty_headers.append(pretty_h)
        
        result = '\r\n'.join([status] + pretty_headers)
        
        return result


class HtmlFormatter(object):

    def format(self, data):
        headers, body = separate_headers_and_body(data)
        
        header_formatter = HttpHeadersFormatter()
        pretty_headers = header_formatter.format(headers)
        
        pretty_body = self._format_body(body)
        
        return pretty_headers + '\r\n\r\n' + pretty_body
    
    def _format_body(self, response_body):
        try:
            tmp = json.loads(response_body)
            response_body = json.dumps(tmp, indent=4)
        
            lexer = JavascriptLexer() # guess_lexer(response_body)
            formatter = PygmentsHtmlFormatter(nowrap=True)
            pretty_response_body = highlight(response_body, lexer, formatter)
        except ValueError:
            # response_body is not JSON
            pretty_response_body = force_escape(response_body)
            
        return pretty_response_body
    


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
