
from django.db import models

from urlparse import urlparse


class HttpSession(models.Model):

    HTTP_METHODS = (
        'DELETE',
        'GET',
        'POST',
        'PUT',
    )
    
    HTTP_METHOD_CHOICES = [(x,x) for x in HTTP_METHODS]

    time_requested = models.DateTimeField(auto_now_add=True)
    time_completed = models.DateTimeField(blank=True, null=True)

    http_method = models.CharField('HTTP method', max_length=200, choices=HTTP_METHOD_CHOICES)
    http_url = models.CharField('HTTP URL', max_length=500)
    
    http_response = models.TextField('HTTP response', blank=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.http_method, self.http_url)
    
    def get_absolute_url(self):
        return '/session/%d' % self.pk
    
    def needs_to_send_request(self):
        return self.time_completed is None
    
    def get_hostname(self):
        parsed = urlparse(self.http_url)
        return parsed.hostname
        
    def get_raw_request(self):
        parsed = urlparse(self.http_url)
        req = '%s %s HTTP/1.1\r\nHost: %s\r\nAccept: */*\r\n\r\n' % (self.http_method, parsed.path, self.get_hostname())
        return req
    
    class Meta:
        verbose_name = 'HTTP session'
