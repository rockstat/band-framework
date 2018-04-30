from jsonrpcserver.aio import methods as _methods
from aiohttp.web import RouteTableDef
from asyncio import sleep

class Tasks(list):
    def add(self, item):
        self.append(item)
        return item


class Registrator:
    def __init__(self):
        self._tasks = Tasks()
        self._router = RouteTableDef()
        print('creating registrator')
    
    @property
    def methods(self):
        return _methods

    @property
    def tasks(self):
        return self._tasks

    @property
    def routes(self):
        return self._router

