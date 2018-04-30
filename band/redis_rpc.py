import jsonrpcclient
from jsonrpcclient.async_client import AsyncClient
from jsonrpcclient.request import Request
from jsonrpcserver.aio import methods
import asyncio
import ujson
import aioredis

from .lib import logger

# Positions in rpc method name
DEST_POS = 0
METHOD_POS = 1
SENDER_POS = 2

class RedisClientAsync(AsyncClient):

    def __init__(self, service, redis_dsn, endpoint='none'):
        super(RedisClientAsync, self).__init__(endpoint)
        self.service = service
        self.pending = {}
        self.redis_dsn = redis_dsn
        self.queue = asyncio.Queue()
        self.timeout = 5

    async def dispatch(self, msg):
        mparts = msg['method'].split(':')
        # call answer
        if 'result' in msg:
            if 'id' in msg and msg['id'] in self.pending:
                self.pending[msg['id']].set_result(msg)
        # method call
        elif 'params' in msg and 'id' in msg and len(mparts) == 3 and mparts[DEST_POS] == self.service:
            response = await methods.dispatch(msg)
            msg['method'] = mparts[METHOD_POS]
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
                service, msg = await self.queue.get()
                try:
                    await pub.publish(service, msg)
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
                ch, *_ = await sub.subscribe('band')
                logger.debug('redis_rpc_reader: entering loop')
                while await ch.wait_message():
                    msg = await ch.get(encoding='utf-8')
                    try:
                        msg = ujson.loads(msg)
                        await self.dispatch(msg)
                    except Exception as error:
                        logger.error(
                            'redis_rpc_reader: dispatching error %s', error)
            except aioredis.ConnectionClosedError:
                logger.debug('redis_rpc_reader: connection closed')
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.debug('redis_rpc_reader: loop cancelled')
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
        self.pending[req_id] = asyncio.Future()
        await asyncio.wait_for(self.pending[req_id], timeout=self.timeout)
        # Retunrning result
        result = self.pending[req_id].result()
        del self.pending[req_id]
        return self.process_response(result)

    async def request(self, to, method, **params):
        req = Request(to+':'+method+':'+self.service, params)
        return await self.send(req, request_id=req['id'], to=to)
