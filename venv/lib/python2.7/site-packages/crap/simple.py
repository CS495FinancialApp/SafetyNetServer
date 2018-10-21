import os

from endpoints.interface.simple import Server


os.environ['ENDPOINTS_PREFIX'] = 'econtroller'
os.environ['ENDPOINTS_SIMPLE_HOST'] = 'localhost:8000'
#os.environ['ENDPOINTS_PREFIX', 'econtroller']

s = Server()
s.serve_count(5)

