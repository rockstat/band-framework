from asyncio import sleep
import aiojobs
from .. import dome

__all__ = ['attach_scheduler']


async def jobs_startup(app):
    app['redis_rpc_writer'] = app.loop.create_task(app['rpc'].writer(app))
    for task in dome.tasks:
        await app['scheduler'].spawn(task())


async def jobs_cleanup(app):
    app['scheduler'].close()


def attach_scheduler(app):
    app.on_startup.append(jobs_startup)
    app.on_shutdown.append(jobs_cleanup)

