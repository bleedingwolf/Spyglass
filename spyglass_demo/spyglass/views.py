
import datetime
import json

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.http import HttpResponse

from spyglass.models import HttpSession
from spyglass.backend import run_session, session_is_ready
from spyglass.formatters import HtmlFormatter, html_line_numbers
from spyglass.forms import HttpSessionForm


def homepage(request):

    f = HttpSessionForm()
    context = {'form': f}
    return render_to_response('spyglass/create_session.html', context, context_instance=RequestContext(request))

def create_session(request):
    
    if request.method == "POST":
    
        f = HttpSessionForm(request.POST)
        if f.is_valid():
            s = HttpSession(http_method=f.cleaned_data['method'],
                http_url=f.cleaned_data['url'],
                follow_redirects=f.cleaned_data['follow_redirects'],
                http_body=f.cleaned_data['body'])
            s.save()
            if s.pk:
                # save was successful
                return redirect(s.get_absolute_url())
            else:
                # something went wrong...
                print "[ERROR] Unable to save HttpSession!"
        else:
            print " [WARN] submitted form was invalid: " + str(f.errors)
    else:
        f = HttpSessionForm()
    
    context = {
        'form': f,
    }
    
    return render_to_response('spyglass/create_session.html', context, context_instance=RequestContext(request))


def session_resend(request, session_id):

    session = get_object_or_404(HttpSession, pk=session_id)
    
    session.id = None
    session.time_requested = datetime.datetime.now()
    session.time_completed = None
    session.http_response = ''
    session.save()
    
    return redirect(session.get_absolute_url())


def session_list(request):
    all_sessions = HttpSession.objects.all().order_by('-time_requested')
    context = {
        'session_list': all_sessions,
        'form': HttpSessionForm()
    }
    return render_to_response('spyglass/session_list.html', context, context_instance=RequestContext(request))


def session_completed_jsonp(request, session_id):

    session = get_object_or_404(HttpSession, pk=session_id)
    ready = session_is_ready(session)
    
    html_formatter = HtmlFormatter()
    response = {'session_id': session.id}
    
    response['complete'] = 'true' if ready else 'false'
    
    if ready:
        if session.http_error:
            response['error'] = session.get_http_error_display()
        else:
            pretty_response = html_formatter.format(session.http_response)
            response['pretty_response'] = pretty_response
            response['response_linenos'] = html_line_numbers(pretty_response)
            response['elapsed_milliseconds'] = (session.time_completed - session.time_requested).microseconds / 1000.0
    
    return HttpResponse(json.dumps(response), mimetype='application/json')


def session_detail(request, session_id):
    
    session = get_object_or_404(HttpSession, pk=session_id)
    html_formatter = HtmlFormatter()

    run_session(session)
    
    pretty_request = html_formatter.format(session.get_raw_request())
    
    if session.time_completed:
        if not session.http_error:
            pretty_response = html_formatter.format(session.http_response)
            session_time = session.time_completed - session.time_requested
            elapsed_milliseconds = session_time.microseconds / 1000.0
    else:
        pretty_response = render_to_string('spyglass/fragment_loading_placeholder.html', {'session_id': session.id})
        elapsed_milliseconds = None
    
    form_values = {
        'url': session.http_url,
        'follow_redirects': session.follow_redirects,
        'method': session.http_method,
    }
    form = HttpSessionForm(form_values)
        
    context = {
        'session': session,
        'pretty_request': pretty_request,
        'pretty_response': pretty_response,
        'request_linenos': html_line_numbers(pretty_request),
        'response_linenos': html_line_numbers(pretty_response),
        'elapsed_milliseconds': elapsed_milliseconds,
        'form': form
    }
    
    return render_to_response('spyglass/session_detail.html', context, context_instance=RequestContext(request))    
