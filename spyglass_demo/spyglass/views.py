
import socket
import datetime

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import force_escape

from spyglass.models import HttpSession
from spyglass.backend import run_session
from spyglass.formatters import HtmlFormatter


def create_session(request):
    
    if request.method == "POST":
    
        s = HttpSession(http_method=request.POST['method'], http_url=request.POST['url'])
        s.save()
        if s.pk:
            # save was successful
            return redirect(s.get_absolute_url())
        else:
            # something went wrong...
            pass

    return render_to_response('spyglass/create_session.html')


def session_resend(request, session_id):

    session = get_object_or_404(HttpSession, pk=session_id)
    
    session.id = None
    session.time_requested = datetime.datetime.now()
    session.time_completed = None
    session.http_response = ''
    session.save()
    
    return redirect(session.get_absolute_url())


def session_detail(request, session_id):
    
    session = get_object_or_404(HttpSession, pk=session_id)
    html_formatter = HtmlFormatter()

    run_session(session) # TODO: this should happen async.
    
    raw_request = session.get_raw_request()
    split_request = raw_request.splitlines()
    request_linenos = '\r\n'.join([str(i+1) for i in xrange(len(split_request))])
    
    pretty_request = html_formatter.format(raw_request)
    pretty_response = html_formatter.format(session.http_response)

    split_response = pretty_response.splitlines()
    response_linenos = '\r\n'.join([str(i+1) for i in xrange(len(split_response))])

    session_time = session.time_completed - session.time_requested
        
    context = {
        'session': session,
        'pretty_request': pretty_request,
        'pretty_response': pretty_response,
        'request_linenos': request_linenos,
        'response_linenos': response_linenos,
        'elapsed_milliseconds': session_time.microseconds / 1000.0,
    }
    
    return render_to_response('spyglass/session_detail.html', context)    
