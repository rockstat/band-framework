from jsonrpcserver.aio import AsyncMethods
from aiohttp.web import RouteTableDef
from collections import UserDict


class Tasks(list):
    def add(self, item):
        self.append(item)
        return self


class AsyncRolesMethods(AsyncMethods):
    def add(self, *args, **kwargs):
        if not hasattr(self, '_roles'):
            self._roles = {}

        def inner(handler):
            name = kwargs.get('name', handler.__name__)
            role = kwargs.get('role', None)
            self._roles.update({name: role})
            self.update({name: handler})
            return handler
        return inner

    @property
    def roles_tups(self):
        return [(k, role,) for k, role in self._roles.items()]


class Dome:
    def __init__(self):
        self._tasks = Tasks()
        self._router = RouteTableDef()
        self._methods = AsyncRolesMethods()

    @property
    def methods(self):
        return self._methods

    @property
    def tasks(self):
        return self._tasks

    @property
    def routes(self):
        return self._router

def smth():
    pass


__all__ = ['Dome', 'smth']