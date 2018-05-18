import logging
import coloredlogs

LOGGER_FORMAT = '%(asctime)s %(levelname)s %(message)s'
coloredlogs.install()
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]', stream=None)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


__all__ = ['logger']
