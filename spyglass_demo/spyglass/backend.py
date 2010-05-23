
def run_session(session):

    if session.needs_to_send_request():
    
        hostname = session.get_hostname()
        print "Making request to %s..." % hostname
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, 80))
        sock.sendall(session.get_raw_request())
        
        receiving_headers = True
        raw_response = ''
        f = sock.makefile()
        
        status = f.readline()
        raw_response += status
        
        headers = {}
        while receiving_headers:
            raw_header = f.readline()
            raw_response += raw_header
            
            if not raw_header.strip():
                receiving_headers = False
                break
            
            header, value = raw_header.split(':', 1)
            header = header.strip().lower()
            value = value.strip()
            headers[header] = value
        
        transfer_coding = headers.get('transfer-encoding', None)
        content_length = headers.get('content-length', None)
        
        print "Transfer coding: %s" % transfer_coding
        print "Content length: %s" % content_length
        
        if transfer_coding == 'chunked':
            while True:
                c = f.readline().strip()
                try:
                    chunk_size = int(c, 16)
                except ValueError:
                    print "Error reading chunk size: %s" % c
                    print "Next Line: %s" % f.readline()
                    continue
                if chunk_size == 0:
                    break
                else:
                    raw_response += f.read(chunk_size)
                    blank = f.readline() # should be blank
                    if blank.strip():
                        print "WARN: chunk ending not CRLF, was %s" % blank
        elif content_length:
            try:
                length = int(content_length)
            except ValueError:
                print "WARN: unable to parse Content-Length header: %s" % content_length
            raw_response += f.read(length)
        
        f.close()
        sock.close()
        
        print "Received %d bytes from host." % len(raw_response)
        
        session.http_response = raw_response
        session.time_completed = datetime.datetime.now()
        session.save()
