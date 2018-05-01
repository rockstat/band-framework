import logging

LOGGER_FORMAT = '%(asctime)s %(levelname)s %(message)s'

logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]', stream=None)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


__all__ = ['logger']
