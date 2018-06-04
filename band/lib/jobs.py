import aiojobs
import inspect
from .. import dome, logger

__all__ = ['attach_scheduler', 'run_task']


async def process_shutdown(app):
    for task in dome.tasks._shutdown:
        try:
            await task()
        except Exception:
            logger.exception('shutdown')


async def scheduler_startup(app):
    logger.info('starting scheduler')
    app['scheduler'] = await aiojobs.create_scheduler(exception_handler=None)

    for task in dome.tasks._startup:
        try:
            if inspect.iscoroutinefunction(task) == True:
                task = task()
            await app['scheduler'].spawn(task)
        except Exception:
            logger.exception('exc')

    app.on_shutdown.append(process_shutdown)


async def scheduler_cleanup(app):

    await app['scheduler'].close()


async def run_task(coro):
    return await app['scheduler'].spawn(coro)


def attach_scheduler(app):
    app.on_startup.append(scheduler_startup)
    app.on_shutdown.append(scheduler_cleanup)
