
# Text statuses
RESULT_OPERATING = 'operating'
RESULT_PONG = 'pong'
RESULT_OK = 'ok'
RESULT_NOT_FOUND = 'not found'
RESULT_INTERNAL_ERROR = 'internal server error'

__all__ = list([v for v  in globals().keys() if not v.startswith('__')])

print(__all__)
