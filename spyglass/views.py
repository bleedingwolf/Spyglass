
import datetime
import os
import django.utils.simplejson as json
from importlib import import_module

import pystache

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import list_detail

from spyglass.models import HttpSession, Plugin
from spyglass.backend import run_session, session_is_ready
from spyglass.formatters import HtmlFormatter, html_line_numbers
from spyglass.forms import session_and_headers_form
from spyglass.viewhelpers import mustache_context_for_session


def plugin_forms(request=None):
    
    forms = []

    all_plugins = Plugin.objects.all()
    for plugin in all_plugins:

        obj = plugin.get_instance()

        if not obj:
            continue

        form = obj.get_form_instance(request)

        if not form:
            continue

        form.plugin = plugin

        forms.append(form)

    return forms


def homepage(request):

    session_form, headers_form = session_and_headers_form()
    context = {'form': session_form, 'http_header_form': headers_form, 'plugin_forms': plugin_forms(request) }
    return render_to_response('spyglass/create_session.html', context, context_instance=RequestContext(request))


def create_session(request):
    
    if request.GET.get('advanced', 'no') == 'yes':
        advanced = True
    else:
        advanced = False
    
    if request.method == "POST":
    
        f, header_formset = session_and_headers_form(request.POST)
        
        if f.is_valid():

            header_text = ''
            if header_formset.is_valid():
                header_text = '\r\n'.join([x.formatted_header() for x in header_formset.forms if x.formatted_header()])
                
            s = HttpSession(http_method=f.cleaned_data['method'],
                http_url=f.cleaned_data['url'],
                http_headers=header_text,
                follow_redirects=f.cleaned_data['follow_redirects'],
                http_body=f.cleaned_data['body'])

                    
            # apply plugins
            all_plugins = Plugin.objects.all()
            applied_plugins = []

            for plugin in all_plugins:

                obj = plugin.get_instance()

                if not obj:
                    continue

                kwargs = {}

                form = obj.get_form_instance(request)

                if form:
                    kwargs['form'] = form

                was_applied = obj.dispatch(request, s, **kwargs)

                if was_applied:
                    applied_plugins.append(plugin)

            s.save()
            s.applied_plugins = applied_plugins
            
            if s.pk:
                # save was successful
                request.session.setdefault('spyglass_session_ids', set()).add(s.pk)
                request.session.modified = True
                
                return redirect(s.get_absolute_url())
            else:
                # something went wrong...
                print "[ERROR] Unable to save HttpSession!"
        else:
            print " [WARN] submitted form was invalid: " + str(f.errors)
    else:
        f, header_formset = session_and_headers_form()
    
    context = {
        'form': f,
        'http_header_form': header_formset,
        'use_advanced_form': advanced,
    }
    
    return render_to_response('spyglass/create_session.html', context, context_instance=RequestContext(request))


def session_resend(request, session_id):

    session = get_object_or_404(HttpSession, pk=session_id)
    
    session.id = None
    session.time_requested = datetime.datetime.now()
    session.time_completed = None
    session.http_response = ''
    session.save()
    
    request.session.setdefault('spyglass_session_ids', set()).add(session.pk)
    request.session.modified = True
    
    return redirect(session.get_absolute_url())


def session_list_generic(request, queryset):

    form, header_form = session_and_headers_form()

    return list_detail.object_list(
        request,
        queryset = queryset,
        paginate_by = 20,
        template_name = 'spyglass/session_list.html',
        template_object_name = 'session',
        extra_context = dict(
            form = form,
            http_header_form = header_form
        )
    )


def session_list_mine(request):
    
    my_session_ids = request.session.get('spyglass_session_ids', set())
    my_sessions = HttpSession.objects.filter(pk__in=my_session_ids).order_by('-time_requested')
        
    return session_list_generic(request, my_sessions)


def session_list_all(request):
    
    all_sessions = HttpSession.objects.all().order_by('-time_requested')
    
    return session_list_generic(request, all_sessions)


def session_completed_jsonp(request, session_id):

    session = get_object_or_404(HttpSession, pk=session_id)
    response = mustache_context_for_session(session)
    
    return HttpResponse(json.dumps(response), mimetype='application/json')


def session_detail(request, session_id):
    
    session = get_object_or_404(HttpSession, pk=session_id)
    html_formatter = HtmlFormatter()

    run_session(session)
    
    pretty_request = html_formatter.format(session.get_raw_request())

    use_advanced_form = (len(session.http_body) != 0) or (len(session.http_headers) != 0)
    form, http_header_form = session_and_headers_form(session=session)

    response_template = open(os.path.join(settings.MEDIA_ROOT, 'mustache/session.mustache')).read()
    formatted_response = pystache.render(response_template, mustache_context_for_session(session))
    
    context = {
        'session': session,
        'pretty_request': pretty_request,
        'request_linenos': html_line_numbers(pretty_request),
        
        'show_placeholder': not session_is_ready(session),
        'formatted_response': formatted_response,
        
        'form': form,
        'http_header_form': http_header_form,
        'use_advanced_form': use_advanced_form,
        'plugin_forms': plugin_forms(request),
    }
    
    return render_to_response('spyglass/session_detail.html', context, context_instance=RequestContext(request))    
