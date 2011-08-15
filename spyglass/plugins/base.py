
from django import forms


class SpyglassPluginForm(forms.Form):

    enabled = forms.BooleanField(initial=False, required=False)


class SpyglassPlugin(object):

    def dispatch(self, django_request, spyglass_session, form=None):

        if form:
            if form.is_valid() and form.cleaned_data['enabled']:
                return self.pre_process_session(django_request, spyglass_session, form)
            else:
                return False
        else:
            return self.pre_process_session(django_request, spyglass_session)
