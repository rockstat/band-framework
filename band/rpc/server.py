from jsonrpcserver.aio import AsyncMethods
from ..constants import ROLES
from ..lib.structs import MethodRegistration

import jsonrpcserver

jsonrpcserver.config.log_requests = False
jsonrpcserver.config.log_responses = False


class AsyncRolesMethods(AsyncMethods):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._roles = dict()

    def add_method(self, handler, registration={}, *args, **kwargs):
        method_name = kwargs.pop('name', handler.__name__)
        role = kwargs.pop('role', None)

        self._roles[method_name] = MethodRegistration(
            method=method_name, role=role, options=registration)
        self[method_name] = handler

    def add(self, *args, **kwargs):
        def wrapper(handler):
            self.add_method(handler, *args, **kwargs)
            return handler
        return wrapper

    @property
    def dicts(self):
        for mc in self._roles.values():
            if mc.role in ROLES and not mc.method.startswith('__'):
                yield mc._asdict()
