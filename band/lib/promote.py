from asyncio import sleep
from .. import (settings, dome, logger, rpc, BAND_SERVICE)


@dome.tasks.add
async def promote():
    logger.info('announcing service')
    while True:
        # Initial delay
        await sleep(1)
        logger.info('promoting service')
        try:
            await rpc.request(BAND_SERVICE, 'promote',
                              name=settings.name)
        except Exception:
            logger.exception('announce error')
        # Notify every 10 min
        await sleep(60*10)


@dome.expose()
async def __status(**params):
    """
    Service status
    """
    
    return {'methods': dome.methods.roles_tups}
