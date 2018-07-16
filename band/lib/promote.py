from asyncio import sleep
from time import time
from datetime import timedelta
from .. import (settings, dome, logger, rpc, DIRECTOR_SERVICE, NOTIFY_ALIVE)

START_AT = round(time() * 1000)


@dome.tasks.add
async def promote():
    logger.info('starting announcing service')
    while True:
        # Initial delay
        await sleep(1)
        try:
            await rpc.notify(
                DIRECTOR_SERVICE, NOTIFY_ALIVE, name=settings.name)
        except Exception:
            logger.exception('announce error')
        # Notify every
        await sleep(5)


@dome.expose()
async def __status(**params):
    """
    Service status
    """
    ms_diff = round(time() * 1000 - START_AT)
    up_time = str(timedelta(milliseconds=ms_diff))
    return {
        'name': settings.name,
        'app_started': START_AT,
        'app_uptime': ms_diff,
        'app_state': 'running',
        'register': dome.methods.dicts
    }
