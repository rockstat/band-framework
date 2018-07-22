import logging
import sys
import coloredlogs
from .config.env import environ
from pprint import pprint

HUMAN_FORMAT = '%(asctime)s %(levelname)s %(message)s'
JSON_FORMAT = '{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "levelNo":"%(levelno)s", "levelName":"%(levelname)s", "message":"%(message)s"}'

logger = logging.getLogger(__name__)

if environ.get('JSON_LOGS', False):
    logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(JSON_FORMAT)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
else:
    coloredlogs.install(level='DEBUG', stream=sys.stdout, fmt=HUMAN_FORMAT),

x__all__ = ['logger']
