from jsonrpcserver.aio import AsyncMethods
from ..lib.structs import MethodRegistration
from ..constants import ROLES
from ..log import logger
import jsonrpcserver

jsonrpcserver.config.log_requests = False
jsonrpcserver.config.log_responses = False
jsonrpcserver.config.trim_log_values = True

# configure_logger(logger, None)

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