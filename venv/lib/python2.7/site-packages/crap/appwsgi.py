#! /usr/bin/env python
import logging

import pout
from endpoints.interface import WSGI

logging.basicConfig()


application = WSGI('testcontroller')
#def application(environ, start_response):
#    pout.v(environ, start_response)
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
