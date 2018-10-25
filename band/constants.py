# roles

LISTENER = 'listener'
HANDLER = 'handler'
ENRICHER = 'enricher'
ROLES = set([LISTENER, ENRICHER, HANDLER])

# Services
DIRECTOR_SERVICE = 'director'
FRONTIER_SERVICE = 'front'

# Text statuses
RESULT_OPERATING = 'operating'
RESULT_PONG = 'pong'
OK = 'o-o-ok'
RESULT_OK = 200
RESULT_NOT_FOUND = 404
RESULT_BAD_ARGS = 404
RESULT_INTERNAL_ERROR = 500
BROADCAST = 'broadcast'
ENRICH = 'enrich'

NOTIFY_ALIVE = '__iamalive'
REQUEST_STATUS = '__status'


HUMA_LOGF = '%(asctime)s %(levelname)s %(message)s'
JSON_LOGF = '{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "levelNo":"%(levelno)s", "levelName":"%(levelname)s", "message":"%(message)s"}'

