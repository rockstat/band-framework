from asyncio import sleep
from .. import (settings, dome, rpc, logger,
                RESULT_OK, BAND_SERVICE, KERNEL_SERVICE)

from .dock_async import Dock

dock = Dock(**settings)
logger.info('Initializing director api')

@dome.tasks.add
async def warmup_dock():
    await dock.inspect_containers()


@dome.expose(path='/run/{name}')
async def service_run(name, **params):
    """
    Create and run new container with service
    """
    return await dock.run_container(name, params)


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
