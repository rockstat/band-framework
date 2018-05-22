import logging
# import coloredlogs

LOGGER_FORMAT = '%(asctime)s %(levelname)s %(message)s'
JSON_FORMAT='{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "fileName":"%(filename)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}'
# coloredlogs.install()

# , datefmt='[%H:%M:%S]'
logging.basicConfig(format=JSON_FORMAT)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


__all__ = ['logger']
