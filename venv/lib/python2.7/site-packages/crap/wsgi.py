#! /usr/bin/env python

# you can call this with:
# uwsgi --http :9000 --wsgi-file wsgi.py --master --processes 1 --thunder-lock --chdir=/vagrant

import os

from endpoints.interface.wsgi import Server


os.environ['ENDPOINTS_PREFIX'] = 'econtroller'
application = Server()


# some code to use python's built in wsgi server
# Our tutorial's WSGI server
#from wsgiref.simple_server import make_server, WSGIRequestHandler
#
#class Handler(WSGIRequestHandler):
#    def __init__(self, *args, **kwargs):
#        pout.h()
#        WSGIRequestHandler.__init__(self, *args, **kwargs)
#        #super(Handler, self).__init__(*args, **kwargs)
#
#    def get_environ(self):
#        pout.h()
#        return super(Handler, self).get_environ()
#
#    def handle(self):
#        pout.h()
#
#def application(environ, start_response):
#    #pout.v(environ, start_response)
#
#    status = '200 OK'
#    response_headers = [('Content-Type', 'text/plain')]
#    start_response(status, response_headers)
#
#    # Sorting and stringifying the environment key, value pairs
#    response_body = ['%s: %s' % (key, value) for key, value in sorted(environ.items())]
#    response_body = '\n'.join(response_body)
#
#    return [response_body]
#
## Instantiate the WSGI server.
## It will receive the request, pass it to the application
## and send the application's response to the client
#httpd = make_server(
#    '127.0.0.1', # The host name.
#    9001, # A port number where to wait for the request.
#    application, # Our application object name, in this case a function.
#    handler_class=Handler
#)
#
## Wait for a single request, serve it and quit.
#httpd.handle_request()
#
