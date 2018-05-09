from asyncio import sleep
from time import time
from collections import defaultdict
from itertools import count
from prodict import Prodict

from .. import (settings, dome, rpc, logger, app,
                RESULT_OK, BAND_SERVICE, KERNEL_SERVICE, NOTIFY_ALIVE, REQUEST_STATUS)

from .dock_async import Dock

dock = Dock(**settings)
logger.info('Initializing director api')


async def run_task(coro):
    return await app['scheduler'].spawn(coro)


class State:
    def __init__(self):
        self._state = dict()

    def ensure_struct(self, name):
        if name not in self._state or not self._state[name]:
            ms = round(time()*1000)
            self._state[name] = Prodict(name=name, init=ms, methods=[])

    def set_status(self, name, status):
        self.ensure_struct(name)
        self._state[name].update(status)

    def exists(self, name):
        return name in self._state and self._state[name] is not None

    async def registrations(self):
        res = []
        for name, state in self._state.items():
            if self.exists(name) and 'methods' in state:
                for method, role in state.methods:
                    res.append([name, method, role])
        return res

    async def lst(self):
        return list(self._state.values())

    async def ls(self):
        return {s.name: s.status for s in self._state.values()}

    async def state_changed(self):
        methods = await self.registrations()
        await rpc.notify(KERNEL_SERVICE, 'services', methods=methods)

    async def unregister(self, name):
        if self.exists(name):
            self._state[name] = None
            await run_task(self.state_changed())

    async def restart_container(self, name):
        await self.unregister(name)
        await dock.restart_container(name)

    async def stop_container(self, name):
        await self.unregister(name)
        res = await dock.stop_container(name)
        return res

    async def remove_container(self, name):
        await self.unregister(name)
        await dock.remove_container(name)

    async def run_container(self, name, params):
        if self.exists(name):
            await self.stop_container(name)
        self.unregister(name)
        info = await dock.run_container(name, params)
        await self.add_container(name, info)

    async def add_container(self, name, info={}):
        self.ensure_struct(name)
        self._state[name].update(info)

    async def alive_service(self, name):
        if name != KERNEL_SERVICE:
            await state.examine_container(name)
        await run_task(self.state_changed())

    async def examine_container(self, name):
        status = await rpc.request(name, REQUEST_STATUS)
        state.set_status(name, status)
        await run_task(self.state_changed())

    async def examine_containers(self):
        for name in self._state.keys():
            await run_task(self.examine_container(name))


state = State()
OK = {'result': RESULT_OK}


@dome.tasks.add
async def warmup_dock():
    for num in count():
        if num == 0:
            for info in await dock.inspect_containers():
                name = info.pop('name')
                await state.add_container(name, info)
            await state.examine_containers()
        await sleep(30)
        


@dome.expose(name=NOTIFY_ALIVE)
async def iamalive(name, **params):
    """
    Accept services promotions
    """
    await state.alive_service(name)
    return OK


@dome.expose(path='/show/{name}')
async def show(name, **params):
    """
    Show container details
    """
    return (await dock.get(name)).attrs


@dome.expose()
async def ls(**params):
    """
    List container and docker status
    """
    return await state.ls()


@dome.expose(name='list')
async def lst(**params):
    """
    Containers with info
    """
    return await state.lst()


@dome.expose(path='/status/{name}')
async def ask_status(name, **params):
    """
    Ask service status
    """
    return await rpc.request(name, REQUEST_STATUS)


@dome.expose(path='/call/{name}/{method}')
async def call(name, method, **params):
    """
    Call service method
    """
    return await rpc.request(name, method, **params)


@dome.expose(path='/run/{name}')
async def run(name, **params):
    """
    Create image and run new container with service
    """
    return await state.run_container(name, params)


@dome.expose(path='/restart/{name}')
async def restart(name, **params):
    """
    Restart service
    """
    return await state.restart_container(name)


@dome.expose(path='/rm/{name}')
async def remove(name, **params):
    """
    Unload/remove service
    """
    return await state.remove_container(name)


@dome.expose(path='/stop/{name}')
async def stop(name, **params):
    """
    HTTP endpoint
    stop container
    """
    return await state.stop_container(name)
