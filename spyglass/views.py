
import datetime
import os
import django.utils.simplejson as json
import socket

import pystache

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import list_detail

from spyglass.models import HttpSession
from spyglass.backend import run_session, session_is_ready
from spyglass.formatters import HtmlFormatter, html_line_numbers
from spyglass.forms import session_and_headers_form
from spyglass.viewhelpers import replace_localhost_hostname, mustache_context_for_session


def homepage(request):

    session_form, headers_form = session_and_headers_form()
    context = {'form': session_form, 'http_header_form': headers_form}
    return render_to_response('spyglass/create_session.html', context, context_instance=RequestContext(request))


def create_session(request):
    
    if request.GET.get('advanced', 'no') == 'yes':
        advanced = True
    else:
        advanced = False
    
    if request.method == "POST":
    
        f, header_formset = session_and_headers_form(request.POST)
        
        if f.is_valid():
        
            # did the user accidentally use the hostname 'localhost'?
            real_hostname = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]
            real_url, corrected = replace_localhost_hostname(f.cleaned_data['url'], real_hostname)
        
            header_text = ''
            if header_formset.is_valid():
                header_text = '\r\n'.join([x.formatted_header() for x in header_formset.forms if x.formatted_header()])
                
            s = HttpSession(http_method=f.cleaned_data['method'],
                http_url=real_url,
                http_headers=header_text,
                follow_redirects=f.cleaned_data['follow_redirects'],
                http_body=f.cleaned_data['body'],
                autocorrected_localhost=corrected)
            s.save()
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
    }
    
    return render_to_response('spyglass/session_detail.html', context, context_instance=RequestContext(request))    
