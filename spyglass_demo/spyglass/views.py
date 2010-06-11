
import datetime

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import force_escape

from spyglass.models import HttpSession
from spyglass.backend import run_session
from spyglass.formatters import HtmlFormatter, html_line_numbers
from spyglass.forms import HttpSessionForm


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
                pass
    else:
        f = HttpSessionForm()
    
    context = {
        'form': f,
    }
    
    return render_to_response('spyglass/create_session.html', context)


def session_resend(request, session_id):

    session = get_object_or_404(HttpSession, pk=session_id)
    
    session.id = None
    session.time_requested = datetime.datetime.now()
    session.time_completed = None
    session.http_response = ''
    session.save()
    
    return redirect(session.get_absolute_url())


def session_list(request):
    all_sessions = HttpSession.objects.all()
    context = {
        'session_list': all_sessions,
    }
    return render_to_response('spyglass/session_list.html', context)


def session_detail(request, session_id):
    
    session = get_object_or_404(HttpSession, pk=session_id)
    html_formatter = HtmlFormatter()

    # TODO: this should happen async.
    run_session(session, follow_redirects=session.follow_redirects)
    
    pretty_request = html_formatter.format(session.get_raw_request())
    pretty_response = html_formatter.format(session.http_response)

    session_time = session.time_completed - session.time_requested
        
    context = {
        'session': session,
        'pretty_request': pretty_request,
        'pretty_response': pretty_response,
        'request_linenos': html_line_numbers(pretty_request),
        'response_linenos': html_line_numbers(pretty_response),
        'elapsed_milliseconds': session_time.microseconds / 1000.0,
        'create_session_form': HttpSessionForm()
    }
    
    return render_to_response('spyglass/session_detail.html', context)    
