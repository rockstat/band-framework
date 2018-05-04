from asyncio import sleep
from time import time
from collections import defaultdict
from prodict import Prodict

from .. import (settings, dome, rpc, logger, app,
                RESULT_OK, BAND_SERVICE, KERNEL_SERVICE, NOTIFY_ALIVE, REQUEST_STATUS)

from .dock_async import Dock

dock = Dock(**settings)
logger.info('Initializing director api')


class State:
    def __init__(self):
        self._state = dict()

    def registrations(self):
        res = []
        for name, state in self._state.items():
            if 'methods' in state:
                for method, role in state.methods:
                    res.append([name, method, role])
        return res

    def ensure_struct(self, name):
        if name not in self._state or not self._state[name]:
            ms = round(time()*1000)
            self._state[name] = Prodict(name=name, init=ms, methods=[])

    def set_status(self, name, status):
        self.ensure_struct(name)
        self._state[name].update(status)
    
    def rm(self, name):
        self._state[name] = None

    def list_(self):
        return list(self._state.values())

    def ls(self):
        return {s.name: s.status for s in self._state.values()}

    async def notify_kernel(self):
        methods = self.registrations()
        await rpc.notify(KERNEL_SERVICE, '__status_receiver', methods=methods)

    async def add_container(self, name, info={}, check_status=False):
        self, self.ensure_struct(name)
        # we don't check containers just started or restarts.
        # check needed when director started
        if check_status:
            await app['scheduler'].spawn(self.ask_state(name))
        self._state[name].update(info)
        

    async def ask_state(self, name):
        status = await rpc.request(name, REQUEST_STATUS)
        state.set_status(name, status)


state = State()


@dome.tasks.add
async def warmup_dock():
    for info in await dock.inspect_containers():
        name = info.pop('name')
        await state.add_container(name, info, check_status=True)
    await sleep(1)
    await state.notify_kernel()


@dome.expose()
async def __status_request(**params):
    """
    Create and run new container with service
    """
    await app['scheduler'].spawn(state.notify_kernel())


@dome.expose(path='/run/{name}')
async def run(name, **params):
    """
    Create image and run new container with service
    """
    state.rm(name)
    info = await dock.run_container(name, params)
    await state.add_container(info.name, info)
    return info


@dome.expose(name=NOTIFY_ALIVE)
async def iamalive(name, **params):
    """
    Accept services promotions
    """
    await state.ask_state(name)
    return {'result': RESULT_OK}


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
    return state.ls()


@dome.expose(name='list')
async def list_(**params):
    """
    Containers with info
    """
    return state.list_()


@dome.expose(path='/status/{name}')
async def ask_status(name, **params):
    """
    Ask service status
    """
    return await rpc.request(name, REQUEST_STATUS)


@dome.expose(path='/restart/{name}')
async def restart(name, **params):
    """
    Restart service
    """
    state.rm(name)
    return await dock.restart_container(name)


@dome.expose(path='/rm/{name}')
async def remove(name, **params):
    """
    Unload/remove service
    """
    state.rm(name)
    return await dock.remove_container(name)


@dome.expose(path='/stop/{name}')
async def stop(name, **params):
    """
    HTTP endpoint
    stop container
    """
    state.rm(name)
    return await dock.stop_container(name)
