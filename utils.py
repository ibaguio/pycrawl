#!/usr/bin/env python
import os
import time
import random

log_dir = "logs/"
xls_dir = "data/"

#creates a log folder if it doesnt exist yet
def checkDirs():
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    print "Created a log folder.."
  else:
    print "Log folder already exist.."
  if not os.path.exists(xls_dir):
    os.makedirs(xls_dir)
    print "Created a data folder.."
  else:
    print "Data folder already exist.."

#pause on every request to not overload the server
def randomPause(verbose=False):
  pause = random.randint(0,3)
  if verbose:
    print "pause %d sec" %(pause)
  time.sleep(pause) 

#wait for user input
#used for debugging
def pause():
    raw_input()

def clearScreen():
    os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )

#given a list of Courses(class) prints it to an output log file
def courseLog(term,courses,dept,totClass):
    t = term.split()
    f = open("logs/"+t[0]+"_"+t[1]+"_"+dept+"_courses.log","a")
    t = "DEPT:\t\t\t%(dept)s\nCOURSES: \t%(coursCount)d\nTot Class: \t%(totClass)d\n"%{'dept':dept,'totClass':totClass,'coursCount': len(courses)}
    for course in courses:
        t += course.printCourseInfo()
    f.write(t)
    f.close()

# Table mapping response codes to messages; entries have the
# form {code: (shortmessage, longmessage)}.
responses = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
          'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}
