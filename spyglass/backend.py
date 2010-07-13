
import socket
import datetime
from urlparse import urlparse
import time

from celery.decorators import task
from celery.result import AsyncResult

from spyglass.models import format_request, HttpRedirect, HttpSession
from spyglass.http import HttpRequestor


def session_is_ready(session):
    result = AsyncResult(session.celery_task_id)
    return result.successful() and session.time_completed


def run_session(session):
    if session.needs_to_send_request() and not session.http_error:
        task = make_session_request.delay(session.id, session.http_url, session.follow_redirects)
        session.celery_task_id = task.task_id
        session.save()
        

@task(serializer='json')
def make_session_request(session_id, url=None, follow_redirects=False, **kwargs):
    
        session = HttpSession.objects.get(pk=session_id)
        logger = make_session_request.get_logger(**kwargs)    
        logger.info("Starting request for session %s" % session.id)

        requestor = HttpRequestor(session, url, logger)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not requestor.start_request(sock):
            return False

        logger.info("Sent request, waiting for response.")
        
        requestor.read_response_headers()
        
        is_redirect, location = requestor.is_redirect_to_location()
        if is_redirect and follow_redirects:
        
            requestor.close()
        
            if location:
                logger.info("Redirected to %s" % location)
            
                HttpRedirect(url=location, session=session).save()
                make_session_request.delay(session.id, location, follow_redirects)
                
                return True
            else:
                logger.error("Response was a redirect, but no Location header was given")
                return False
        
        requestor.read_body()       
        requestor.close()
        
        session.http_response = requestor.complete_response_text()
        session.time_completed = datetime.datetime.now()
        session.save()
        return True
