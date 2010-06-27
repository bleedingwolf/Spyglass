
from django.db import models

from urlparse import urlparse


def format_request(method, hostname, path, body='', extra_headers=''):

    request_line = '%s %s HTTP/1.1\r\n' % (method, path)
    headers = 'Host: %s\r\nAccept: */*\r\n' % hostname

    if body:
        content_length = len(body)
        headers += 'Content-Length: %d\r\n' % content_length

    headers += extra_headers
    if not headers[-2:] == '\r\n':
        headers += '\r\n'
    
    return request_line + headers + '\r\n' + body


class HttpSession(models.Model):

    HTTP_METHODS = (
        'GET',
        'POST',
        'PUT',
        'DELETE',
    )
    
    HTTP_METHOD_CHOICES = [(x,x) for x in HTTP_METHODS]

    HTTP_ERROR_CHOICES = (
        (0, 'No Error'),
        (1, 'Unknown Host'),
        (2, 'Unspecified Socket Error'),
    )

    time_requested = models.DateTimeField(auto_now_add=True)
    time_completed = models.DateTimeField(blank=True, null=True)

    http_method = models.CharField('HTTP method', max_length=20, choices=HTTP_METHOD_CHOICES)
    http_url = models.CharField('HTTP URL', max_length=500)
    http_headers = models.TextField('HTTP headers', blank=True)
    http_body = models.TextField('HTTP body', blank=True)
    follow_redirects = models.BooleanField(default=True)
    
    http_error = models.PositiveIntegerField('HTTP error', default=0, choices=HTTP_ERROR_CHOICES)
    http_response = models.TextField('HTTP response', blank=True)
    
    celery_task_id = models.CharField(max_length=64, default='')
    
    def __unicode__(self):
        return u'%s %s' % (self.http_method, self.http_url)
    
    def get_absolute_url(self):
        return '/sessions/%d' % self.pk
    
    def needs_to_send_request(self):
        return self.time_completed is None
    
    def get_hostname(self):
        parsed = urlparse(self.http_url)
        return parsed.hostname
        
    def get_raw_request(self, url=None):
        parsed = urlparse(url or self.http_url)
        
        path = parsed.path or '/'
        qs = parsed.query or ''
        if qs:
            path = path + '?' + qs
        
        hostname = parsed.hostname
        return format_request(self.http_method, hostname, path, self.http_body, self.http_headers)
    
    def header_list(self):
        '''
        Returns a list of dicts representing this request's headers.
        '''
        split_headers = [h.split(':') for h in self.http_headers.splitlines()]
        list_of_dicts = [{'name': n.strip(), 'value': v.strip()} for n, v in split_headers]
        return list_of_dicts
    
    class Meta:
        verbose_name = 'HTTP session'


class HttpRedirect(models.Model):

    session = models.ForeignKey(HttpSession)
    url = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'redirected to %s' % self.url
    
    class Meta:
        verbose_name = 'HTTP redirect'
