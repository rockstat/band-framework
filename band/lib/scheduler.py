import aiojobs
import inspect
from .. import logger


class Scheduler:
    def __init__(self, **kwargs):
        self.scheduler = None

    async def startup(self):
        self.scheduler = await aiojobs.create_scheduler(exception_handler=None)

    async def shutdown(self):
        await self.scheduler.close()

    async def spawn(self, coro):
        return await self.scheduler.spawn(coro)

    async def spawn_tasks(self, tasks):
        for task in tasks:
            try:
                logger.debug(f'Executing worker {task.__name__}')
                if inspect.iscoroutinefunction(task) == True:
                    task = task()
                await self.scheduler.spawn(task)
            except Exception:
                logger.exception('exc')
