from asyncio import sleep
from time import time
from datetime import timedelta
from .. import (settings, dome, logger, rpc, BAND_SERVICE, NOTIFY_ALIVE)

START_AT = round(time()*1000)


@dome.tasks.add
async def promote():
    logger.info('announcing service')
    while True:
        # Initial delay
        await sleep(1)
        logger.info('promoting service')
        try:
            await rpc.notify(BAND_SERVICE, NOTIFY_ALIVE, name=settings.name)
        except Exception:
            logger.exception('announce error')
        # Notify every 10 min
        await sleep(60*10)


@dome.expose()
async def __status(**params):
    """
    Service status
    """

    ms_diff = round(time()*1000 - START_AT)
    up_time = str(timedelta(milliseconds=ms_diff))
    return {
        'app_started': START_AT,
        'app_uptime': ms_diff,
        'app_uptime_h': up_time,
        'methods': dome.methods.roles_tups
    }
