from aiohttp import web
import uvloop
import asyncio

from . import dome
from .rpc import RedisPubSubRPC
from .lib import logger, pick

__all__ = ['run_server']

async def startup_tasks(app):
    app['rrpc_w'] = app.loop.create_task(app['rpc'].writer(app))
    app['rrpc_r'] = app.loop.create_task(app['rpc'].reader(app))

async def cleanup_tasks(app):
    for key in ['rrpc_r', 'rrpc_w']:
        app[key].cancel()
        await app[key]

def run_server(http_port, bind_addr, name, **kwargs):

    print(kwargs)

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = web.Application(loop=loop, logger=logger)
    rpc = RedisPubSubRPC(name=name, **pick(kwargs, 'redis_dsn'))
    
    deps = [('rpc', rpc,)]

    # if is_master:
        # deps.append(('dock', dock,))
    
    
    app.update(dict(deps))
    
    app.router.add_routes(dome.routes)
    app.on_startup.append(startup_tasks)
    app.on_shutdown.append(cleanup_tasks)

    web.run_app(app, host=bind_addr,
                port=http_port, handle_signals=True)
