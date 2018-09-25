__VERSION__ = '0.7.1'

import importlib
import os

from .constants import *
from .config.configfile import settings
from .log import *
from .lib.response import BandResponse

response = BandResponse()

logger.info('final configuration', settings=settings)

from .lib.structs import *
from .lib.http import json_response
from .lib.redis import RedisFactory
redis_factory = RedisFactory(**settings)

from .registry import Dome, Expose, worker, cleanup
dome = Dome.instance()
expose: Expose = dome.exposeour

from .server import app, start_server, add_routes
from .rpc.redis_pubsub import RedisPubSubRPC
from .bootstrap import run_task, attach_scheduler, attach_redis_rpc


attach_scheduler(app)
rpc = attach_redis_rpc(app, **settings)

# if settings.name != DIRECTOR_SERVICE:
importlib.import_module('band.promote', 'band')

# libs
from asimplech import ClickHouse
