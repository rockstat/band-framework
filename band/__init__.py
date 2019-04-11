__VERSION__ = '0.17.9'

import importlib
import os
import uvloop
import asyncio


def loop_exc(loop, context):
    message = context.get('message', None)
    exception = context.get('exception', None)
    exc_info = (type(exception), exception,
                exception.__traceback__) if exception else None
    logger.exception('loop ex', message=message,
                     exception=exception, exc_info=exc_info)


loop = uvloop.new_event_loop()
loop.set_exception_handler(loop_exc)
asyncio.set_event_loop(loop)

from .constants import *
from .config.configfile import settings
from .log import *
from .lib import response

# response = BandResponse()

logger.info('final configuration', settings=settings)

from .lib.structs import *
from .lib.http import json_response
from .lib.redis import RedisFactory
redis_factory = RedisFactory(**settings, loop=loop)

from .registry import Dome, Expose, worker, cleanup, blocking
dome: Dome = Dome.instance()
expose: Expose = dome.exposeour

from .server import app, start_server, add_routes
from .lib.scheduler import Scheduler

scheduler = dome['scheduler'] = Scheduler(**settings, loop=loop)

from .rpc.rpc_pubsub_redis import RedisPubSubRPC

app.on_startup.append(dome.on_startup)
app.on_shutdown.append(dome.on_shutdown)

rpc = dome['rpc'] = RedisPubSubRPC(**settings)

# if settings.name != DIRECTOR_SERVICE:
importlib.import_module('band.promote', 'band')

# 3rd party lib re-export
from aiocron import crontab
