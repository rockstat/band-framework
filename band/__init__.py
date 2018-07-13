import importlib
import os

from .constants import *
from .config.env import *
from .log import *
from .config.configfile import settings
from .lib.structs import *
from .lib.http import resp
from .lib.redis import RedisFactory
redis_factory = RedisFactory(**settings)

from .dome import dome
from .server import app, start_server, add_routes
from .lib.jobs import attach_scheduler, run_task
from .lib.redis_pubsub import attach_redis_rpc

rpc = attach_redis_rpc(app, **settings)
attach_scheduler(app)

# if settings.name != DIRECTOR_SERVICE:
importlib.import_module('band.lib.promote', 'band')

__VERSION__ = '0.1.0'
