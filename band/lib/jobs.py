import aiojobs
import inspect
from .. import dome, logger

__all__ = ['attach_scheduler', 'run_task']


async def dome_startup_tasks(app):
    """
    Starting funcs marked as tasks
    """
    for task in dome.tasks._startup:
        try:
            if inspect.iscoroutinefunction(task) == True:
                task = task()
            await app['scheduler'].spawn(task)
        except Exception:
            logger.exception('exc')


async def dome_shutdown_tasks(app):
    """
    Stutdown funcs marked as tasks
    """
    for task in dome.tasks._shutdown:
        try:
            await task()
        except Exception:
            logger.exception('shutdown')


async def scheduler_startup(app):
    """
    Starting tasks executor
    """
    logger.info('Starting "aiojobs" Scheduler')
    app['scheduler'] = await aiojobs.create_scheduler(exception_handler=None)
    # statung custom tasks from implemented services
    await dome_startup_tasks(app)


async def scheduler_cleanup(app):
    # stopping user and system tasks
    await dome_shutdown_tasks(app)
    # stopping scheduler
    await app['scheduler'].close()


async def run_task(coro):
    return await app['scheduler'].spawn(coro)

def attach_scheduler(app):
    app.on_startup.append(scheduler_startup)
    app.on_shutdown.append(scheduler_cleanup)

