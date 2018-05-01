import aiojobs
import inspect
from .. import dome, logger

__all__ = ['attach_scheduler']


async def scheduler_startup(app):
    app['scheduler'] = await aiojobs.create_scheduler()
    logger.info('starting scheduler')
    for task in dome.tasks:
        print(inspect.iscoroutinefunction(task))
        if inspect.iscoroutinefunction(task) == True:
            await app['scheduler'].spawn(task)
        else:
            await app['scheduler'].spawn(task)


async def scheduler_cleanup(app):
    app['scheduler'].close()


def attach_scheduler(app):
    app.on_startup.append(scheduler_startup)
    app.on_shutdown.append(scheduler_cleanup)

