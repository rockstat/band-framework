import importlib
import os

from .constants import *
from .config.configfile import settings
from .log import *

logger.info('final configuration', settings=settings)

from .lib.structs import *
from .lib.http import json_response
from .lib.redis import RedisFactory
redis_factory = RedisFactory(**settings)

from .dome import *
from .server import app, start_server, add_routes
from .lib.jobs import attach_scheduler, run_task
from .lib.redis_pubsub import attach_redis_rpc

attach_scheduler(app)
rpc = attach_redis_rpc(app, **settings)

# if settings.name != DIRECTOR_SERVICE:
importlib.import_module('band.lib.promote', 'band')

# libs

from asimplech import ClickHouse
