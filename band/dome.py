import jsonrpcserver
from collections import deque
from jsonrpcserver.aio import AsyncMethods
from aiohttp.web import RouteTableDef, RouteDef
from prodict import Prodict
from .lib.http import resp
from .log import logger

# jsonrpcserver.config.debug = False
# jsonrpcserver.config.log_requests = False
# jsonrpcserver.config.log_responses = False


class Tasks():
    def __init__(self):
        self._startup = deque()
        self._shutdown = deque()

    def add(self, item):
        self._startup.append(item)
        return self

    def shutdown(self, item):
        self._shutdown.append(item)
        return self


class AsyncRolesMethods(AsyncMethods):
    def add_method(self, handler, *args, **kwargs):
        if not hasattr(self, '_roles'):
            self._roles = Prodict()
        name = kwargs.get('name', handler.__name__)
        role = kwargs.get('role', None)
        self._roles[name] = role
        self[name] = handler

    def add(self, *args, **kwargs):
        if not hasattr(self, '_roles'):
            self._roles = Prodict()

        def inner(handler):
            self.add_method(handler, *args, **kwargs)
            return handler

        return inner

    @property
    def tups(self):
        return [(
            fn,
            role,
        ) for fn, role in self._roles.items() if not fn.startswith('__')]


class Dome:

    NONE = 'none'
    TASK = 'task'
    LISTENER = 'listener'
    HANDLER = 'handler'
    ENRICHER = 'enricher'

    def __init__(self):
        self._tasks = Tasks()
        self._router = RouteTableDef()
        self._routes = []
        self._methods = AsyncRolesMethods()
        self._state = Prodict()

    def expose_method(self, handler, path=None, **kwargs):
        role = kwargs.pop('role', self.NONE)
        name = kwargs.get('name', handler.__name__)
        if path is None:
            path = '/{}'.format(name)

        self._methods.add_method(handler, name=name, role=role)

        async def get_handler(request):
            query = dict(request.query)
            query.update(request.match_info)
            result = await handler(**query)
            return resp(result)

        async def post_handler(request):
            post = await request.post()
            query = dict(request.query)
            query.update(post)
            query.update(request.match_info)
            result = await handler(**query)
            return resp(result)

        self._routes.append(RouteDef('GET', path, get_handler, kwargs))
        self._routes.append(RouteDef('POST', path, post_handler, kwargs))

    def expose(self, *args, **kwargs):
        def inner(handler):
            self.expose_method(handler, *args, **kwargs)
            return handler

        return inner

    def startup(self, *args, **kwargs):
        self._tasks.add(*args, **kwargs)

    def shutdown(self, *args, **kwargs):
        self._tasks.shutdown(*args, **kwargs)

    @property
    def state(self):
        return self._state

    @property
    def methods(self):
        return self._methods

    @property
    def tasks(self):
        return self._tasks

    @property
    def routes(self):
        return self._routes


def smth():
    pass


dome = Dome()

__all__ = ['Dome', 'dome']
