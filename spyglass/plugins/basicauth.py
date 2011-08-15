
from django import forms
import base64

from spyglass.plugins.base import SpyglassPluginForm, SpyglassPlugin


class BasicAuthForm(SpyglassPluginForm):

    username = forms.CharField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)


class BasicAuthPlugin(SpyglassPlugin):

    def plugin_form(self):
        return BasicAuthForm

    def pre_process_session(self, django_request, spyglass_session, form):

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        value_to_encode = '%s:%s' % (username, password)
        header_value = base64.b64encode(value_to_encode)
        header = 'Authorization: Basic %s' % header_value
        spyglass_session.http_headers += header + '\n'

        return True

