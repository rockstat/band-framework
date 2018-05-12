import aiojobs
import inspect
from .. import dome, logger

__all__ = ['attach_scheduler']


async def scheduler_startup(app):
    app['scheduler'] = await aiojobs.create_scheduler()
    logger.info('starting scheduler')
    try:
        for task in dome.tasks:
            # print(inspect.iscoroutinefunction(task))
            # print(type(task))
            if inspect.iscoroutinefunction(task) == True:
                task = task()
            await app['scheduler'].spawn(task)
    except Exception:
        logger.exception('exc')

async def scheduler_cleanup(app):
    await app['scheduler'].close()


def attach_scheduler(app):
    app.on_startup.append(scheduler_startup)
    app.on_shutdown.append(scheduler_cleanup)

