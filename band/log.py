import logging
import sys
import coloredlogs

LOGGER_FORMAT = '%(asctime)s %(levelname)s %(message)s'
JSON_FORMAT='{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "fileName":"%(filename)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}'


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', fmt=JSON_FORMAT, stream=sys.stdout)

# logger.setLevel(logging.DEBUG)
# logging.basicConfig(, datefmt='[%H:%M:%S]')

__all__ = ['logger']
