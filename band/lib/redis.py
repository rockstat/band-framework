from band import settings
import asyncio
import aioredis
from weakref import WeakKeyDictionary

class RedisFactory:
    def __init__(self, redis_dsn, **kwargs):
        self.redis_dsn = redis_dsn
        self.wmap = WeakKeyDictionary()

    async def create_client(self):
        return await aioredis.create_redis(self.redis_dsn)

    # async def create_subsribed_client(self, chan):
    #     client = await self.create_client()
    #     channel, = await client.subscribe(chan)
    #     self.wmap[client] = [chan]
    #     return client, channel

    async def create_pool(self):
        return await aioredis.create_pool(self.redis_dsn)

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
