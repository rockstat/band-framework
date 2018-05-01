from aiohttp import web
import uvloop
import asyncio

from .log import logger

__all__ = ['add_routes', 'start_server', 'app']

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

app = web.Application(loop=loop, logger=logger)


def add_routes(routes):
    app.router.add_routes(routes)


def start_server(http_port, bind_addr, name, **kwargs):

    web.run_app(app, host=bind_addr,
                port=http_port, handle_signals=True)

