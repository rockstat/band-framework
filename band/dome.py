import ujson
import jsonrpcserver
from jsonrpcserver.aio import AsyncMethods
from aiohttp.web import RouteTableDef, RouteDef
from collections import deque
# from prodict import Prodict
from .lib.http import resp
from .log import logger
from .lib.structs import MethodRegistration

jsonrpcserver.config.log_requests = False
jsonrpcserver.config.log_responses = False


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._roles = dict()

    def add_method(self, handler, reg_options={}, *args, **kwargs):
        method_name = kwargs.pop('name', handler.__name__)
        role = kwargs.pop('role', None)
        method_cfg = dict(
            MethodRegistration(method_name, role,
                               reg_options.copy())._asdict())
        self._roles[method_name] = method_cfg
        self[method_name] = handler

    def add(self, *args, **kwargs):
        def inner(handler):
            self.add_method(handler, *args, **kwargs)
            return handler

        return inner

    @property
    def dicts(self):
        return list(method_cfg for method_cfg in self._roles.values()
                    if not method_cfg['method'].startswith('__'))


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

    def expose_method(self,
                      handler,
                      path=None,
                      alias=None,
                      keys=[],
                      props={},
                      register={},
                      **kwargs):
        role = kwargs.pop('role', self.NONE)
        routekwargs = kwargs.pop('route', {})
        name = kwargs.get('name', handler.__name__)
        if path is None:
            path = '/{}'.format(name)
        # Handling frontier registration
        reg_options = dict(**register)
        reg_options['keys'] = keys
        reg_options['props'] = props
        if alias:
            reg_options['alias'] = alias
        if role == Dome.ENRICHER and len(keys) == 0:
            raise ValueError
        self._methods.add_method(
            handler, name=name, role=role, reg_options=reg_options)

        async def get_handler(request):
            query = dict(request.query)
            query.update(request.match_info)
            result = await handler(**query)
            return resp(result, request=request)

        async def post_handler(request):
            query = dict(request.query)
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    raw = await request.text()
                    query.update(ujson.loads(raw))
                else:
                    post = await request.post()
                    query.update(post)
            # url params
            query.update(request.match_info)
            result = await handler(**query)
            return resp(result, request=request)

        self._routes.append(RouteDef('GET', path, get_handler, routekwargs))
        self._routes.append(RouteDef('POST', path, post_handler, routekwargs))

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
