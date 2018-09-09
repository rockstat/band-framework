import ujson
import aiojobs

from prodict import Prodict as pdict

from .lib.http import add_http_handler
from .log import logger
from .lib.helpers import none_none
from .constants import ENRICHER, HANDLER, LISTENER, ROLES
from .rpc.server import AsyncRolesMethods


class Dome:

    __instance = None

    @staticmethod
    def instance():
        if Dome.__instance == None:
            Dome.__instance = Dome()
        return Dome.__instance

    def __init__(self):
        self._executor = None
        self._startup = list()
        self._shutdown = list()
        self._routes = []
        self._methods = AsyncRolesMethods()
        self._expose = None

    def expose_method(self,
                      handler,
                      role,
                      name=None,
                      path=None,
                      keys=None,
                      props=None,
                      alias=None,
                      **kwargs):
        name = name or handler.__name__
        path = path or f'/{name}'

        if role == ENRICHER and not keys:
            raise ValueError('Keys property must be present')

        reg = none_none(dict(
            keys=keys,
            props=props,
            alias=alias
        ))

        self._methods.add_method(
            handler, name=name, role=role, reg=reg)

        self._routes += add_http_handler(handler, path)

    @property
    def exposeour(self):
        if not self._expose:
            self._expose = Expose(self)
        return self._expose

    def expose(self, *args, **kwargs):
        """
        Deprecated API method. Will be removed soon!s
        """
        def inner(handler):
            logger.warn(f"Called {handler.__name__}.Deprecated API method. Will be removed soon!")
            self.expose_method(handler, *args, **kwargs)
            return handler
        return inner

    def add_startup(self, task):
        self._startup.append(task)

    def add_shutdown(self, task):
        self._shutdown.append(task)

    @property
    def startup(self):
        return self._startup

    @property
    def shutdown(self):
        return self._shutdown

    @property
    def methods(self):
        return self._methods

    @property
    def routes(self):
        return self._routes


class Expose:
    def __init__(self, dome):
        self._dome = dome

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
            self._dome.expose_method(
                handler, name=name, path=path, role=HANDLER)
            return handler
        return wrapper

    def __call__(self, *args, **kwargs):
        def wrapper(handler):
            self._dome.expose_method(handler, role=None, *args, **kwargs)
            return handler
        return wrapper

    def enricher(self, props: list, keys: list):
        """
        Expose function and promote function as request enricher to front service
        props: list contains requests props in dot notation like ["sess.type"]
        keys: list of requested dispatching keys
        """
        def wrapper(handler):
            self._dome.expose_method(
                handler, props=[*props], keys=[*keys], role=ENRICHER)
            return handler
        return wrapper

    def listener(self):
        """
        Expose function and promote functions as request listener to front service
        Will receive all requests at final stage
        """
        def wrapper(handler):
            self._dome.expose_method(handler, role=LISTENER)
            return handler
        return wrapper


def worker():
    """
    Register function as worker.
    Will be executed on application startup
    """
    def wrapper(handler):
        logger.info(f"Registered worker {handler.__name__}")
        Dome.instance().add_startup(handler)
        return handler
    return wrapper


def cleanup():
    """
    Register function as unload handler.
    Will be executed on application shutdown
    """
    def wrapper(handler):
        logger.info(f"Registered cleaner {handler.__name__}")
        Dome.instance().add_shutdown(handler)
        return handler
    return wrapper


__all__ = ['Dome']
