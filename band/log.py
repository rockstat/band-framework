import logging
import sys
import coloredlogs
from .config.env import environ
from pprint import pprint

HUMAN_FORMAT = '%(asctime)s %(levelname)s %(message)s'
JSON_FORMAT = '{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "fileName":"%(filename)s", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}'

logger = logging.getLogger(__name__)

if environ.get('HUMANIZE_LOGS', False):
    coloredlogs.install(level='DEBUG', stream=sys.stdout, fmt=HUMAN_FORMAT),
else:
    logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(JSON_FORMAT)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

# logger.setLevel(logging.DEBUG)
# logging.basicConfig(, datefmt='[%H:%M:%S]')

__all__ = ['logger']
