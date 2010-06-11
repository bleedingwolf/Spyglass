
from django import forms

from spyglass.models import HttpSession


class HttpSessionForm(forms.Form):
    method = forms.ChoiceField(choices=HttpSession.HTTP_METHOD_CHOICES, initial='GET')
    url = forms.URLField(initial='http://', widget=forms.TextInput(attrs={'class': 'url-input'}))
    follow_redirects = forms.BooleanField(initial=True, required=False)
    body = forms.CharField(required=False, widget=forms.Textarea)
