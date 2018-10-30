from jsonrpcserver.aio import AsyncMethods
from collections import MutableMapping
from ..lib.structs import MethodRegistration
from ..constants import ROLES

import jsonrpcserver

jsonrpcserver.config.log_requests = False
jsonrpcserver.config.log_responses = False

class RPCServer(MutableMapping):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = dict()
        self._option = dict()

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def __delitem__(self, key):
        del self._state[key]

    def __len__(self):
        return len(self._state)

    def __iter__(self):
        return iter(self._state)

    def add_method(self, handler, options={}, *args, **kwargs):
        method_name = kwargs.pop('name', handler.__name__)
        role = kwargs.pop('role', None)

        self._option[method_name] = MethodRegistration(
            method=method_name, role=role, options=options)
        self[method_name] = handler
    
    async def dispatch(self, msg):
        if msg['method']:
            method = msg['method']
            if method in self:
                return await self[method](**msg['params'])


class AsyncRPCMethods(AsyncMethods):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._roles = dict()

    def add_method(self, handler, options={}, *args, **kwargs):
        method_name = kwargs.pop('name', handler.__name__)
        role = kwargs.pop('role', None)

        self._roles[method_name] = MethodRegistration(
            method=method_name, role=role, options=options)
        self[method_name] = handler

    @property
    def dicts(self):
        """
        Generator for registrations as dicts
        """
        for mc in self._roles.values():
            if mc.role in ROLES and not mc.method.startswith('__'):
                yield mc._asdict()

    def __contains__(self, key):
        return key in self._items