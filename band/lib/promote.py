import asyncio

from ..constants import KERNEL_SERVICE
from ..log import logger

async def promote(name, rpc, methods):
    logger.info('announcing service')
    while True:
        await asyncio.sleep(1)
        try:
            await rpc.request(KERNEL_SERVICE, 'service_register',
                              name=name,
                              methods=methods.roles_tups)
        except Exception:
            logger.exception('announce error')

        await asyncio.sleep(10000)

