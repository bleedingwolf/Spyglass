
import datetime
import django.utils.simplejson as json

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import force_escape
from django.template.loader import render_to_string
from django.http import HttpResponse

from spyglass.models import HttpSession
from spyglass.backend import run_session, session_is_ready
from spyglass.formatters import HtmlFormatter, html_line_numbers
from spyglass.forms import session_and_headers_form


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
        
            header_text = ''
            if header_formset.is_valid():
                header_text = '\r\n'.join([x.formatted_header() for x in header_formset.forms if x.formatted_header()])
                
            s = HttpSession(http_method=f.cleaned_data['method'],
                http_url=f.cleaned_data['url'],
                http_headers=header_text,
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
    
    return redirect(session.get_absolute_url())


def session_list(request):
    all_sessions = HttpSession.objects.all().order_by('-time_requested')
    form, header_form = session_and_headers_form()
    context = {
        'session_list': all_sessions,
        'form': form,
        'http_header_form': header_form,
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
    
    use_advanced_form = (len(session.http_body) != 0) or (len(session.http_headers) != 0)
    form, http_header_form = session_and_headers_form(session=session)
        
    context = {
        'session': session,
        'pretty_request': pretty_request,
        'pretty_response': pretty_response,
        'request_linenos': html_line_numbers(pretty_request),
        'response_linenos': html_line_numbers(pretty_response),
        'elapsed_milliseconds': elapsed_milliseconds,
        'form': form,
        'http_header_form': http_header_form,
        'use_advanced_form': use_advanced_form,
    }
    
    return render_to_response('spyglass/session_detail.html', context, context_instance=RequestContext(request))    
