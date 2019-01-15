from functools import partial
import asyncio
import concurrent.futures
from . import loop, logger


def blocking(params=None):
    """
    Mark function for thread execution
    """

    def wrapper(handler):
        logger.info(f"Wrap block {handler.__name__}")
        async def caller(*args, **kwargs):
            wrapped = partial(handler, *args, **kwargs)
            logger.info('Executing task in custom process')
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, wrapped)
                return result

        return caller

    return wrapper
