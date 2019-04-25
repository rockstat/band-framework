import sys
import ujson
import logging
import structlog
from .lib.helpers import env_is_true
from .lib.json import json_def, json_dumps
from pythonjsonlogger import jsonlogger


def dumper(*args, **kwargs):
    kwargs.pop('default', None)
    kwargs['ensure_ascii'] = False
    return json_dumps(*args, **kwargs)


logging.basicConfig(level=logging.DEBUG, format="%(message)s")
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setFormatter(jsonlogger.JsonFormatter())


processors = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    # structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    # structlog.processors.UnicodeDecoder(),
    # structlog.stdlib.render_to_log_kwargs,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
]


if env_is_true('JSON_LOGS'):
    processors.append(structlog.processors.JSONRenderer(serializer=dumper))
    pass

else:
    processors.append(structlog.dev.ConsoleRenderer())


structlog.configure(
    processors=processors,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    # cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


x__all__ = ['logger']
