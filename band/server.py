from aiohttp import web
import uvloop
import asyncio

from .log import logger
from . import dome

__all__ = ['add_routes', 'start_server', 'app']

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

app = web.Application(logger=logger, debug=False)


def add_routes(routes):
    app.router.add_routes(routes)


def start_server(listen, name, **kwargs):
    host, port = listen.split(':')
    add_routes(dome.routes)

    web.run_app(app, host=host,
                port=port, handle_signals=True, print=None)

