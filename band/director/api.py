from asyncio import sleep
from time import time
from collections import defaultdict
from prodict import Prodict

from .. import (settings, dome, rpc, logger, app,
                RESULT_OK, BAND_SERVICE, KERNEL_SERVICE)

from .dock_async import Dock

dock = Dock(**settings)
logger.info('Initializing director api')


class State:
    def __init__(self):
        self._state = defaultdict(Prodict)
        self.now = lambda: round(time()*1000)
        
    def registrations(self):
        res = []
        for name, state in self._state.items():
            for method, role in state.methods:
                res.append([name, method, role])
        return res

    def set_methods(self, name, methods):
        self._state[name].methods = methods
        self._state[name].ts = self.now()

    async def notify_kernel(self):
        methods = self.registrations()
        await rpc.request(KERNEL_SERVICE, 'service_register', methods=methods)
        

    async def countainer_found(self, name, info={}):
        self._state[name].info = info
        await app['scheduler'].spawn(self.ask_state(name))

    async def ask_state(self, name):
        status = await rpc.request(name, '__status')
        if 'methods' in status:
            print(status['methods'])
            state.set_methods(name, status['methods'])


state = State()


@dome.tasks.add
async def warmup_dock():
    names = await dock.inspect_containers()
    for name in names:
        await state.countainer_found(name)
    await sleep(1)
    await state.notify_kernel()
    print(state._state)


@dome.expose()
async def __registrations(**params):
    """
    Create and run new container with service
    """
    await app['scheduler'].spawn(state.notify_kernel())


@dome.expose(path='/run/{name}')
async def service_run(name, **params):
    """
    Create and run new container with service
    """
    return await dock.run_container(name, params)


@dome.expose(path='/promote')
async def promote(*, name):
    """
    Accept services promotions
    """
    await state.ask_state(name)
    return {'result': RESULT_OK}


@dome.expose(path='/show/{name}')
async def service_ping(name, **params):
    """
    Show container details
    """
    return (await dock.get(name)).attrs


@dome.expose()
async def index(**params):
    """
    HTTP endpoint
    list containers
    """
    return await dock.conts_list()


@dome.expose(path='/ask_status/{name}')
async def ask_status(name, **params):
    """
    Ask service status
    """
    return await rpc.request(name, 'status')


@dome.expose(path='/restart/{name}')
async def restart(name, *params):
    """
    Restart service
    """
    return await dock.restart_container(name)


@dome.expose(path='/remove/{name}')
async def unload(name, *params):
    """
    Unload/remove service
    """
    return await dock.remove_container(name)


@dome.expose(path='/stop/{name}')
async def stop(name, **params):
    """
    HTTP endpoint
    stop container
    """
    return await dock.stop_container(name)
