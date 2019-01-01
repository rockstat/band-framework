from band import settings
import asyncio
import aioredis
from aioredis.pool import ConnectionsPool
from .. import logger
# from weakref import WeakKeyDictionary

class RedisFactory:
    def __init__(self, redis_dsn='redis://host:6379/0', loop=None, **kwargs):
        self.redis_dsn = redis_dsn
        self.loop = loop
        # self.wmap = WeakKeyDictionary()

    async def create_client(self):
        logger.debug('creating redis client using to', redis_dns=self.redis_dsn)
        return await aioredis.create_redis(self.redis_dsn, loop=self.loop)

    # async def create_subsribed_client(self, chan):
    #     client = await self.create_client()
    #     channel, = await client.subscribe(chan)
    #     self.wmap[client] = [chan]
    #     return client, channel

    async def create_pool(self):
        logger.debug('creating redis pool using to', redis_dns=self.redis_dsn)
        return await aioredis.create_pool(self.redis_dsn, loop=self.loop)

    async def create_redis_pool(self, **kwargs):
        return await aioredis.create_redis_pool(self.redis_dsn, loop=self.loop, **kwargs)

    async def close_client(self, client):
        # if client in self.wmap:
        #     for chan in self.wmap[client]:
        #         await self.wmap[client].unsubscribe(chan)
        if not client.closed:
            client.close()
            await client.wait_closed()
        # await asyncio.sleep(0)

    async def close_pool(self, pool):
        pool.close()
        await pool.wait_closed()
        await asyncio.sleep(0.01)
