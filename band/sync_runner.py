from functools import partial
import asyncio
import concurrent.futures
from . import loop, logger


def blocking(params=None):
    """
    Mark function for thread execution
    """

    def wrapper(handler):
        logger.info(f"rapping blocking function {handler.__name__}")
        logger.debug('W')

        async def caller(*args, **kwargs):
            wrapped = partial(handler, *args, **kwargs)
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, wrapped)
                print('custom thread pool', result)
                return result

        return caller

    return wrapper
