from band import settings
import asyncio
import aioredis


class RedisFactory:
    def __init__(self, redis_dsn, **kwargs):
        self.redis_dsn = redis_dsn

    async def create_client(self):
        return await aioredis.create_redis(self.redis_dsn)

    async def create_pool(self):
        return await aioredis.create_pool(self.redis_dsn)

    async def close_client(self, client):
        client.close()
        await client.wait_closed()
        await asyncio.sleep(0.01)

    async def close_pool(self, pool):
        pool.close()
        await pool.wait_closed()
        await asyncio.sleep(0.01)
