import os
import logging
import sys

from endpoints.interface.mongrel2 import Server

# configure root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(stream=sys.stderr)
log_formatter = logging.Formatter('[%(levelname)s] %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

os.environ['ENDPOINTS_MONGREL2_SUB'] = "tcp://127.0.0.1:9001"
os.environ['ENDPOINTS_MONGREL2_PUB'] = "tcp://127.0.0.1:9002"
os.environ['ENDPOINTS_PREFIX'] = 'econtroller'

s = Server()
s.serve_forever()

