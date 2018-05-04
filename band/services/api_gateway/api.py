import subprocess
import os.path
import aiohttp
from aiohttp import ClientConnectorError
import asyncio
import aiojobs
from prodict import Prodict
from band import app, dome, logger, settings, RESULT_INTERNAL_ERROR, RESULT_NOT_LOADED_YET


rucaptcha_base = 'https://rucaptcha.com/res.php'

"""
"""


async def do_query(url, params):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=10, params=params) as r:
                return await r.json()
    except Exception:
        logger.exception('err')
    return RESULT_INTERNAL_ERROR


@dome.expose(role=dome.HANDLER)
async def balance(**params):
    params = {
        'key': settings.rucaptcha_key,
        'action': 'getbalance',
        'json': 1
    }
    return {
        'result': await do_query(rucaptcha_base, params)
    }
