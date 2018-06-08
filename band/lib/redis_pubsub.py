from jsonrpcclient.async_client import AsyncClient
from jsonrpcclient.request import Request, Notification
from async_timeout import timeout
from collections import namedtuple
import asyncio
import ujson
import itertools
import aioredis
from aioredis.pubsub import Receiver
from aioredis.abc import AbcChannel

from .. import dome, logger, BROADCAST

# Positions in rpc method name
DEST_POS = 0
METHOD_POS = 1
SENDER_POS = 2


class MethodCall(namedtuple('MethodCall', ['dest', 'method', 'source'])):
    __slots__ = ()

    def tos(self):
        return self.dest + ':' + self.method + ':' + self.source

    def __repr__(self):
        return self.dest + ':' + self.method + ':' + self.source

    @classmethod
    def make(cls, method):
        return cls._make(method.split(':'))


class RedisPubSubRPC(AsyncClient):
    def __init__(self, name, app, redis_dsn, endpoint='none', **kwargs):
        super(RedisPubSubRPC, self).__init__(endpoint)
        self.name = name
        self._app = app
        self._loop = app.loop
        self.pending = {}
        self.redis_dsn = redis_dsn
        self.redis_params = kwargs.get("redis_params", {})
        self.channels = [self.name]
        if 'listen_all' in self.redis_params and self.redis_params['listen_all'] == True:
            self.channels.append(BROADCAST)
        self.queue = asyncio.Queue()
        self.timeout = 5
        self.id_gen = itertools.count(1)

    async def dispatch(self, msg):
        """
        add handling
        {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params"}, "id": "1"}
        """
        # common extension
        if 'method' in msg:
            mparts = msg['method'].split(':')
            if len(mparts) == 3:
                msg['to'] = mparts[0]
                msg['method'] = mparts[1]
                msg['from'] = mparts[2]
        # answer
        if 'result' in msg:
            # logger.debug('received with result: %s', msg)
            if 'id' in msg and msg['id'] in self.pending:
                self.pending[msg['id']].set_result(msg)
        # call to served methods
        elif 'params' in msg:
            # check address structure
            if msg['to'] == self.name or msg['to'] == BROADCAST:
                response = await dome.methods.dispatch(msg)
                if not response.is_notification:
                    await self.put(msg['from'], ujson.dumps(response))
                    
    async def chan_reader(self, chan):
        logger.info('starting reader for channel %s', chan)
        while True:
            try:
                sub = await aioredis.create_redis(self.redis_dsn, loop=self._loop)
                channel, = await sub.subscribe(chan)
                while True:
                    msg = await channel.get(encoding='utf-8')
                    if msg is None:
                        break
                    msg = ujson.loads(msg)
                    await self._app['scheduler'].spawn(self.dispatch(msg))
            except Exception:
                logger.exception('reader finished')
            except asyncio.CancelledError:
                break
                logger.info('redis_rpc_reader: loop cancelled / call break')
            finally:
                sub.close()
                await sub.wait_closed()
                await asyncio.sleep(1)

    async def reader(self):
        for chan in self.channels:
            asyncio.ensure_future(self.chan_reader(chan))

    async def writer(self):
        while True:
            logger.info('redis_rpc_writer: root loop. creating pool')
            try:
                pool = await aioredis.create_pool(
                                    self.redis_dsn, loop=self._loop)
                logger.info('redis_rpc_writer: entering loop')
                while True:
                    name, msg = await self.queue.get()
                    self.queue.task_done()
                    async with pool.get() as conn:
                        await conn.execute('publish', name, msg)                            

            except asyncio.CancelledError:
                logger.info('redis_rpc_writer: cancelled / break')
                break
            except Exception:
                logger.exception('redis_rpc_writer: unknown')
            finally:
                logger.info('redis_rpc_writer: finally / closing pool')
                pool.close()
                await pool.wait_closed()
                await asyncio.sleep(1)

    async def get(self):
        item = await self.queue.get()
        self.queue.task_done()
        return item

    async def request(self, to, method, **params):
        mc = MethodCall(dest=to, method=method, source=self.name)
        req_id = str(next(self.id_gen))
        req = Request(mc.tos(), params, request_id=req_id)
        return await self.send(req, request_id=req['id'], to=to)

    async def notify(self, to, method, **params):
        mc = MethodCall(dest=to, method=method, source=self.name)
        req = Notification(mc.tos(), **params)
        return await self.send(req, to=to)

    async def put(self, dest, data):
        await self.queue.put((
            dest,
            data,
        ))

    async def send_message(self, request, **kwargs):
        to = kwargs['to']
        # Outbound msgs queue
        await self.put(to, request.encode())
        # skip waiting for notification
        if 'request_id' not in kwargs:
            return
        # Waiting for response
        req_id = kwargs['request_id']
        try:
            req = self.pending[req_id] = asyncio.Future()
            # await asyncio.wait_for(self.pending[req_id], timeout=self.timeout)
            async with timeout(2) as cm:
                await req
        except asyncio.TimeoutError:
            logger.error('rpc.send_message TimeoutError. to: %s ; id %s', to,
                         req_id)
        except asyncio.CancelledError:
            logger.error('CancelledError')
        finally:
            del self.pending[req_id]

        # Retunrning result
        return None if cm.expired else self.process_response(req.result())


# Attaching to aiohttp
async def redis_rpc_startup(app):
    app['rrpc_w'] = asyncio.ensure_future(app['rpc'].writer())# app.loop.create_task(app['rpc'].writer())
    app['rrpc_r'] = asyncio.ensure_future(app['rpc'].reader())# app.loop.create_task(app['rpc'].reader())


async def redis_rpc_cleanup(app):
    app['rrpc_r'].cancel()
    await app['rrpc_r']
    app['rrpc_w'].cancel()
    await app['rrpc_w']


def attach_redis_rpc(app, name, **kwargs):
    rpc = app['rpc'] = RedisPubSubRPC(name=name, app=app, **kwargs)
    app.on_startup.append(redis_rpc_startup)
    app.on_shutdown.append(redis_rpc_cleanup)
    return rpc


__all__ = ['RedisPubSubRPC', 'attach_redis_rpc']
