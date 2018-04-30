from asyncio import sleep

from band import dome, logger, settings, KERNEL_SERVICE

__all__ = ['announce_api']

@dome.tasks.add
async def announce_api(app):
    await sleep(1)
    while True:
        try:
            rpc = app['rpc']
            await rpc.request(KERNEL_SERVICE, 'service_register',
                              name=settings.name,
                              methods=dome.methods.roles_tups)
            # logger.debug('registration result = %s', reg_res)
        except Exception:
            logger.exception('announce error')

        await sleep(10)

