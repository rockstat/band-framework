import importlib

from .constants import *
from .log import *
from .lib.structs import *
from .lib.http import *
from .config import *
from .dome import *
from .server import *
from .lib.jobs import attach_scheduler
from .lib.redis_pubsub import attach_redis_rpc
from .lib.promote import promote

rpc = attach_redis_rpc(app, **settings)
attach_scheduler(app)

if settings.master:
    importlib.import_module('band.director', 'band')

else:
    importlib.import_module('band.services.{}'.format(settings.name), 'band')
    dome.tasks.append(promote(settings.name, rpc, dome.methods))

add_routes(dome.routes)
