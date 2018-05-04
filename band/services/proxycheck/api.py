import subprocess
import os.path
import aiohttp
from aiohttp import ClientConnectorError
import asyncio
import aiojobs
from collections import Counter
from random import random
from prodict import Prodict
from band import app, dome, logger, settings, RESULT_INTERNAL_ERROR, RESULT_NOT_LOADED_YET

class State(dict):
    def __init__(self):
        self.loop = 0
        self.iteration = 0
        self.success = 0

    def myloop(self):
        self.loop += 1
        self.iteration = 0
        self.success = 0

    def myiter(self):
        self.iteration += 1

    def succ(self):
        self.success +=1

    def myget(self):
        return {
            'loop': self.loop,
            'iteration': self.iteration,
            'success': self.success
        }

state = State()
test_url = 'https://m.vk.com/'
check_ip = 'https://ipinfo.io/ip'
copyattrs = 'geoId id host port user type usage geoId alias status'.split(' ')
CONCURRENT_CHECKS = 3

"""


"""

async def chech(p, params):
    asyncio.sleep(random()*1)
    check = Prodict(success=0, region=p.cityRu)
    check.update({k: p[k] for k in copyattrs})
    try:
        state.myiter()
        async with aiohttp.ClientSession() as chs:
            proxy_auth = aiohttp.BasicAuth(p.user, p.password)
            hostport = f"http://{p.host.strip()}:{p.port}"
            async with chs.get(test_url, proxy=hostport, proxy_auth=proxy_auth, timeout=10) as pr:
                check.responseCode = pr.status
                if pr.status == 200:
                    check.success = 1
                    check.contentSize = len(await pr.text())
            async with chs.get(check_ip, proxy=hostport, proxy_auth=proxy_auth, timeout=10) as ip_r:                                
                if ip_r.status == 200:
                    check.extIp = (await ip_r.text()).strip()
                    state.succ()
    except ClientConnectorError:
        logger.warn('connection error: %s:%s', p.host, p.port) 
    except TimeoutError:
        logger.warn('timeout') 
    except Exception:
        logger.exception('check err')
    await asyncio.sleep(1)
    try:
        async with aiohttp.ClientSession() as ss:
            async with ss.post(params.notify, json=check, timeout=10) as wh_r:
                if wh_r.status != 200:
                    logger.error('webhook failed')
    except Exception:
        logger.exception('sending webhook err')


@dome.tasks.add
async def checker():
    scheduler = await aiojobs.create_scheduler(limit=CONCURRENT_CHECKS)
    while True:
        state.myloop()
        try:
            params = settings.proxy_checker
            headers = {"Authorization": params.auth}
            async with aiohttp.ClientSession(headers=headers) as s:
                async with s.get(params.list, timeout=5) as r:
                    for proxy in await r.json():
                        p = Prodict.from_dict(proxy)
                        await scheduler.spawn(chech(p, params))                     
        except Exception:
            logger.exception('err')
        jobs = scheduler._jobs
        while True:
            await asyncio.sleep(0.1)
            if len(jobs) == 0:
                logger.info('finished')
                break      


@dome.expose()
async def progress(**params):
    try:
        return {'result': state.myget()}
    except Exception:
        logger.exception('err')
    return {'result': RESULT_INTERNAL_ERROR}
