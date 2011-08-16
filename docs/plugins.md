
## Plugin Basics

A plugin must be on the Python path, and must have a matching `spyglass.Plugin` entry in the database. Plugin classes should subclass the provided `spyglass.plugins.base.SpyglassPlugin` class.

The Plugin object contains a human-readable name and the classname of the plugin. For example, the built-in "Fix Localhost" plugin has the name "Fix Localhost" and the class name `spyglass.plugins.localhost.LocalhostPlugin`. The human-readable name will be presented to users on the session form and on the session detail pages.

A plugin may optionally specify a Django form class to be used to collect parameters from the user. This form should subclass the provided `spyglass.plugins.base.SpyglassPluginForm` class.

## The Plugin API

A Spyglass plugin must implement at least one method: `pre_process_session`, which takes at least two arguments. The first is the Django `HttpRequest` object for the incoming browser request, the second is the Spyglass `HttpSession` object that is about to be saved to the database.

If the plugin implements a method named `plugin_form `, Spyglass will use the returned form class to prompt the user for parameters. The form will be passed back to the plugin as a third argument to `pre_process_session`.

The plugin has the opportunity to modify the `HttpSession` before it's saved, modifying any attributes it wants. If the plugin has performed any work, the `pre_process_session` method should return `True`. This causes a notification to appear on the session detail page, informing the user that their request was modified by a plugin.

## Simple Plugins

A simple plugin is always enabled. Creating a simple plugin is as easy as subclassing the base class. The example below will add a "User-Agent" header to every outgoing request.

    # file: example.py
    from spyglass.plugins.base import SpyglassPlugin

    class Plugin(SpyglassPlugin):

        def pre_process_session(self, django_request, spyglass_session):
            user_agent_header = "User-Agent: Spyglass/1.0\n"
            spyglass_session.http_headers += user_agent_header
            return True

## Advanced Plugins

Plugins that require input from the user can specify a form class to be presented. For example, the following example plugin implements HTTP basic auth, which requires the user to provide a username and password.
    
    # basic auth example
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
