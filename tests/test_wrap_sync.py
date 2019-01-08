import json
import ujson
import os
import pytest
from time import sleep
from itertools import count

from band import blocking, loop, logger
import asyncio


@blocking()
def blocking_func(seconds):
    logger.info(f'starting sleep {seconds}')
    sleep(seconds)
    logger.info(f'end of sleep {seconds}')
    return seconds


async def nonblock_func(seconds):
    logger.info(f'starting nonblock sleep {seconds}')
    for c in count():
        if c == seconds/0.05:
            return c
        await asyncio.sleep(0.045)
        logger.info('puk ', c=c)


def test_wrap_sync():
    f = asyncio.gather(nonblock_func(1), blocking_func(1))
    res = loop.run_until_complete(f)
    assert res == [20, 1]


if __name__ == '__main__':
    test_wrap_sync()


