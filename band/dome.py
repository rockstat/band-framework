import ujson
import jsonrpcserver
from jsonrpcserver.aio import AsyncMethods
from aiohttp.web import RouteTableDef, RouteDef
from .lib.http import json_response, json_middleware, request_handler
from .log import logger
from .lib.structs import MethodRegistration

jsonrpcserver.config.log_requests = False
jsonrpcserver.config.log_responses = False

LISTENER = 'listener'
HANDLER = 'handler'
ENRICHER = 'enricher'
NONE = 'none'


class Tasks():
    def __init__(self):
        self._startup = list()
        self._shutdown = list()

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

        self._roles[method_name] = MethodRegistration(
            method=method_name, role=role, options=reg_options)
        self[method_name] = handler

    def add(self, *args, **kwargs):
        def wrapper(handler):
            self.add_method(handler, *args, **kwargs)
            return handler
        return wrapper

    @property
    def dicts(self):
        for method_cfg in self._roles.values():
            if method_cfg.role != Dome.NONE and not method_cfg.method.startswith('__'):
                yield method_cfg._asdict()


class Dome:
    NONE = 'none'
    TASK = 'task'
    LISTENER = LISTENER
    HANDLER = HANDLER
    ENRICHER = ENRICHER

    def __init__(self):
        self._tasks = Tasks()
        self._router = RouteTableDef()
        self._routes = []
        self._methods = AsyncRolesMethods()

    def expose_method(self,
                      handler,
                      path=None,
                      alias=None,
                      keys=None,
                      props=None,
                      register=None,
                      role=NONE,
                      **kwargs):
        routekwargs = kwargs.pop('route', {})
        name = kwargs.get('name', None)
        if not name:
            name = handler.__name__
        if path is None:
            path = f'/{name}'
        # Handling frontier registration
        reg_options = dict(**(register or {}))
        reg_options['keys'] = keys or []
        reg_options['props'] = props or {}
        if alias and alias != None:
            reg_options['alias'] = alias
        if role == Dome.ENRICHER and len(keys) == 0:
            raise ValueError('Keys property must be present')
        self._methods.add_method(
            handler, name=name, role=role, reg_options=reg_options)

        async def wrapper(request):
            return await request_handler(request, handler)

        logger.info('Adding route', path=path,
                    wrap=wrapper, routekwargs=routekwargs)
        self._routes.append(
            RouteDef('GET', path, wrapper, routekwargs))
        self._routes.append(
            RouteDef('POST', path, wrapper, routekwargs))

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


class Expose:

    def __init__(self, dome):
        self.dome = dome

    def handler(self, name=None, path=None, alias=None):
        """
        Expose function and promote function as request handler to front service.
        name: 
        path="/hello/:name" For services exposed by HTTP you can configure path with with params
        alias=other_service If needed possible to promote service by different name. Affected only service name in front service
        """
        print(name, path, alias)

        def wrapper(handler):
            print(handler)
            self.dome.expose_method(
                handler, name=name, path=path, role=HANDLER)
            return handler
        return wrapper

    def enricher(self, props: list, keys: list):
        """
        Expose function and promote function as request enricher to front service
        props: list contains requests props in dot notation like ["sess.type"]
        keys: list of requested dispatching keys
        """
        def wrapper(handler):
            self.dome.expose_method(
                handler, props=[*props], keys=[*keys], role=ENRICHER)
            return handler
        return wrapper

    def listener(self):
        """
        Expose function and promote functions as request listener to front service
        Will receive all requests at final stage
        """
        def wrapper(handler):
            self.dome.expose_method(handler, role=LISTENER)
            return handler
        return wrapper

    def __call__(self, *args, **kwargs):
        def wrapper(handler):
            self.dome.expose_method(handler, role=NONE, *args, **kwargs)
            return handler
        return wrapper


def worker(*args, **kwargs):
    """
    Register function as worker.
    Will be executed on application startup
    """
    def wrapper(handler):
        dome._tasks.add(handler)
        return handler
    return wrapper


def cleaner(*args, **kwargs):
    """
    Register function as cleaner.
    Will be executed on application shotdown
    """
    def wrapper(handler):
        dome._tasks.shutdown(handler)
        return handler
    return wrapper


dome = Dome()
expose = Expose(dome)


__all__ = ['Dome', 'dome', 'expose', 'worker', 'cleaner']
