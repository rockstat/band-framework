from asyncio import sleep
from .. import (settings, dome, rpc, logger,
                RESULT_OK, BAND_SERVICE, KERNEL_SERVICE)

from .dock import Dock

dock = Dock(**settings)
logger.info('Initializing director api')


@dome.expose(path='/run/{name}')
async def service_run(name, **params):
    """
    Create and run new container with service
    """
    return dock.run_container(name, params)


@dome.expose(path='/ping/{name}')
async def service_ping(name, **params):
    """
    Ping service
    """
    return dock.ping(name)


@dome.expose()
async def list(**params):
    """
    HTTP endpoint
    list containers
    """
    return dock.containers_list()


@dome.expose(path='/ask_status/{name}')
async def ask_status(name, **params):
    """
    Ask service status
    """
    return await rpc.request(name, 'status')


@dome.expose(path='/unload/{name}')
async def unload(name, *params):
    """
    Unload/remove service
    """
    return dock.remove_container(name)


@dome.expose(path='/stop/{name}')
async def stop(name, request):
    """
    HTTP endpoint
    stop container
    """
    return dock.stop_container(name)
