
from django import forms


class SpyglassPluginForm(forms.Form):

    enabled = forms.BooleanField(initial=False, required=False)


class SpyglassPlugin(object):

    def __init__(self):
        self.plugin_id = 0

    def dispatch(self, django_request, spyglass_session, form=None):

        if form:
            if form.is_valid() and form.cleaned_data['enabled']:
                return self.pre_process_session(django_request, spyglass_session, form)
            else:
                return False
        else:
            return self.pre_process_session(django_request, spyglass_session)

    def get_form_instance(self, request=None):
        if hasattr(self, 'plugin_form'):
            form_klazz = self.plugin_form()
            if request and request.method == 'POST':
                form = form_klazz(request.POST, prefix='plugin-%d' % self.plugin_id)
            else:
                form = form_klazz(prefix='plugin-%d' % self.plugin_id)
            return form

        return None
