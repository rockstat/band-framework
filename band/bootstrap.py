import aiojobs
import inspect
from . import dome, app, logger
from .rpc.redis_pubsub import RedisPubSubRPC


# Attaching to aiohttp
async def redis_rpc_startup(app):
    await app['scheduler'].spawn(app['rpc'].writer())
    await app['scheduler'].spawn(app['rpc'].reader())


async def scheduler_startup(app):
    """
    Starting scheduler and funcs marked as tasks
    """
    logger.info('Starting scheduler')
    app['scheduler'] = await aiojobs.create_scheduler(exception_handler=None)
    logger.info('Starting startup handlers')
    for task in dome.startup:
        try:
            logger.debug(f'Executing worker {task.__name__}')
            if inspect.iscoroutinefunction(task) == True:
                task = task()
            await app['scheduler'].spawn(task)
        except Exception:
            logger.exception('exc')


async def scheduler_shutdown(app):
    """
    Stutdown funcs marked as tasks
    """
    logger.info('Stopping shutdown handlers')
    for task in dome.shutdown:
        try:
            logger.debug(f'Executing cleaner {task.__name__}')
            await task()
        except Exception:
            logger.exception('shutdown')
    # stopping scheduler
    logger.info('Stopping scheduler')
    await app['scheduler'].close()


async def run_task(coro):
    return await app['scheduler'].spawn(coro)


def attach_redis_rpc(app, name, **kwargs):
    logger.info('Attaching redis RPC')
    rpc = app['rpc'] = RedisPubSubRPC(name=name, app=app, **kwargs)
    app.on_startup.append(redis_rpc_startup)
    return rpc


def attach_scheduler(app):
    logger.info('Attaching scheduler')
    app.on_startup.append(scheduler_startup)
    app.on_shutdown.append(scheduler_shutdown)
