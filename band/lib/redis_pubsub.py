from jsonrpcclient.async_client import AsyncClient
from jsonrpcclient.request import Request
from async_timeout import timeout
import asyncio
import ujson
import aioredis

from .. import dome
from .. import logger


# Positions in rpc method name
DEST_POS = 0
METHOD_POS = 1
SENDER_POS = 2

class RedisPubSubRPC(AsyncClient):
    def __init__(self, name, redis_dsn, endpoint='none', **kwargs):
        super(RedisPubSubRPC, self).__init__(endpoint)
        self.name = name
        self.pending = {}
        self.redis_dsn = redis_dsn
        self.queue = asyncio.Queue()
        self.timeout = 5

    async def dispatch(self, msg):
        mparts = msg['method'].split(':')
        print(mparts)
        # call answer
        if 'result' in msg:
            # logger.debug('received with result: %s', msg)
            if 'id' in msg and msg['id'] in self.pending:
                self.pending[msg['id']].set_result(msg)
        # method call
        elif 'params' in msg and 'id' in msg and len(mparts) == 3 and mparts[DEST_POS] == self.name:            
            msg['method'] = mparts[METHOD_POS]
            response = await dome.methods.dispatch(msg)
            if not response.is_notification:
                await self.put(mparts[SENDER_POS], ujson.dumps(response))

    async def get(self):
        item = await self.queue.get()
        self.queue.task_done()
        return item

    async def put(self, dest, data):
        await self.queue.put((dest, data,))

    async def writer(self, app):
        try:
            pub = await aioredis.create_redis_pool(self.redis_dsn, loop=app.loop)
            logger.info('redis_rpc_writer: entering loop')
            while True:
                name, msg = await self.queue.get()
                # logger.debug('publishing to %s: %s', name, msg)
                try:
                    await pub.publish(name, msg)
                except Exception as error:
                    logger.error('redis_rpc_writer: error %s', error)

        except asyncio.CancelledError:
            logger.info('redis_rpc_writer: cancelled')
            pass
        finally:
            await pub.quit()

    async def reader(self, app):
        while True:
            try:
                sub = await aioredis.create_redis(self.redis_dsn, loop=app.loop)
                ch, *_ = await sub.subscribe(self.name)
                logger.info('redis_rpc_reader: entering loop')
                while await ch.wait_message():
                    msg = await ch.get(encoding='utf-8')
                    try:
                        msg = ujson.loads(msg)
                        await self.dispatch(msg)
                    except Exception as error:
                        logger.error(
                            'redis_rpc_reader: dispatching error %s', error)
            except aioredis.ConnectionClosedError:
                logger.error('redis_rpc_reader: connection closed')
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info('redis_rpc_reader: loop cancelled')
                break
            except Exception as error:
                logger.error('redis_rpc_reader: unknown error %s', error)
                await asyncio.sleep(1)
            finally:
                if not sub.closed:
                    await sub.unsubscribe(ch.name)
                    await sub.quit()

    async def send_message(self, request, **kwargs):
        req_id = kwargs['request_id']
        to = kwargs['to']
        # Outbound msgs queue
        await self.put(to, request.encode())
        # Waiting for response
        try:
            req = self.pending[req_id] = asyncio.Future()
            # await asyncio.wait_for(self.pending[req_id], timeout=self.timeout)
            async with timeout(2) as cm:
                await req
        # except asyncio.TimeoutError:
        #     logger.error('TimeoutError')
        finally:
            del self.pending[req_id]
        
        # Retunrning result
        return self.process_response(req.result())
        

    async def request(self, to, method, **params):
        req = Request(to+':'+method+':'+self.name, params)
        return await self.send(req, request_id=req['id'], to=to)


# Attaching to aiohttp

async def redis_rpc_startup(app):
    app['rrpc_w'] = app.loop.create_task(app['rpc'].writer(app))
    app['rrpc_r'] = app.loop.create_task(app['rpc'].reader(app))


async def redis_rpc_cleanup(app):
    for key in ['rrpc_r', 'rrpc_w']:
        app[key].cancel()
        await app[key]

def attach_redis_rpc(app, name, **kwargs):

    rpc = app['rpc'] = RedisPubSubRPC(name=name, **kwargs)
    app.on_startup.append(redis_rpc_startup)
    app.on_shutdown.append(redis_rpc_cleanup)
    return rpc


__all__ = ['RedisPubSubRPC', 'attach_redis_rpc']

