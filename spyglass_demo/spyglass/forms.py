
from django import forms
from django.forms.formsets import formset_factory

from spyglass.models import HttpSession


class HttpSessionForm(forms.Form):

    method = forms.ChoiceField(choices=HttpSession.HTTP_METHOD_CHOICES, initial='GET',
        widget=forms.Select(attrs={'class': 'spyglass-dropdown'}))
        
    url = forms.CharField(initial='http://',
        widget=forms.TextInput(attrs={'class': 'url-input'}))
        
    follow_redirects = forms.BooleanField(initial=True, required=False)
    
    body = forms.CharField(required=False,
        widget=forms.Textarea)


class HttpHeaderForm(forms.Form):

    name = forms.CharField()
    value = forms.CharField()
    
    def formatted_header(self):
        try:
            return '%s: %s' % (self.cleaned_data['name'], self.cleaned_data['value'])
        except KeyError:
            return ''

HttpHeaderFormset = formset_factory(HttpHeaderForm, extra=1)

def session_and_headers_form(params=None, session=None):
    if params:
        return HttpSessionForm(params), HttpHeaderFormset(params, prefix='header')
    elif session:
        form_values = {
            'url': session.http_url,
            'follow_redirects': session.follow_redirects,
            'method': session.http_method,
            'body': session.http_body
        }
        return HttpSessionForm(initial=form_values), HttpHeaderFormset(initial=session.header_list(), prefix='header')
    else:
        return HttpSessionForm(), HttpHeaderFormset(prefix='header')
