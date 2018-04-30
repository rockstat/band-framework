from collections import deque, defaultdict, UserDict
import logging

LOGGER_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]', stream=None)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Text statuses
RESULT_OPERATING = 'operating'
RESULT_PONG = 'pong'
RESULT_OK = 'ok'
RESULT_NOT_FOUND = 'not found'
RESULT_INTERNAL_ERROR = 'internal server error'

# Services
BAND_SERVICE = 'band'
KERNEL_SERVICE = 'kernel'

class DotDict(UserDict):
    def __getattr__(self, attr):
        attr = self.get(attr, None)
        return DotDict(attr) if type(attr) == dict else attr

def pick(d, *keys):
    return {k: getattr(d, k) for k in keys}


