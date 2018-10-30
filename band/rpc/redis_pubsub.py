"""
This module containt components for JSON2-RPC-like protocol implementation
used to interract with side parts of platform.
"""

from jsonrpcclient.async_client import AsyncClient
from jsonrpcclient.request import Request, Notification
from async_timeout import timeout
from collections import namedtuple
from prodict import Prodict
import asyncio
import ujson
import itertools

from .. import logger, redis_factory, dome, scheduler, BROADCAST, ENRICH


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
    """
    Band RPC interface. 
    Used to interract with other microservices

    Class constants:
    RPC_TIMEOUT Default timeout for RPC request (seconds)
    """

    RPC_TIMEOUT = 2

    def __init__(self, name, rpc_params=None, redis_params=None,
                 **kwargs):
        super(RedisPubSubRPC, self).__init__('noop')
        self.name = name
        self.pending = {}
        # TODO: remove redis_params
        if redis_params:
            logger.warn(
                'Variable redis_params deprecated and will be removed. Use rpc_params instead.'
            )
        self.rpc_params = Prodict.from_dict(rpc_params or redis_params or {})
        self.channels = set([self.name])
        if self.rpc_params.listen_all == True:
            self.channels.add(BROADCAST)
        if self.rpc_params.listen_enrich == True:
            self.channels.add(ENRICH)
        self.queue = asyncio.Queue()
        self.id_gen = itertools.count(1)

    def log_request(self, request, extra=None, fmt=None, trim=False):
        pass

    def log_response(self, response, extra=None, fmt=None, trim=False):
        pass

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
        if 'result' in msg or 'error' in msg:
            # logger.debug('received with result', msg=msg)
            if 'id' in msg and msg['id'] in self.pending:
                self.pending[msg['id']].set_result(msg)
        # call exposed method
        elif 'params' in msg:
            # check address structure
            if msg['to'] in self.channels:
                response = await dome.methods.dispatch(msg)
                if not response.is_notification:
                    resp = {**response, 'from': self.name, 'to': msg['from']}
                    await self.put(msg['from'],
                                   ujson.dumps(resp, ensure_ascii=False))

    async def reader(self):
        for chan in self.channels:
            await scheduler.spawn(self.chan_reader(chan))

    async def chan_reader(self, chan):
        logger.info('starting reader for channel', chan=chan)
        while True:
            try:
                client = await redis_factory.create_client()
                channel, = await client.subscribe(chan)
                while True:
                    msg = await channel.get(encoding='utf-8')
                    if msg is None:
                        break
                    msg = ujson.loads(msg)
                    await scheduler.spawn(self.dispatch(msg))
            except asyncio.CancelledError:
                logger.info('redis_rpc_reader: loop cancelled / call break')
                break
            except Exception:
                logger.exception('reader exception')
                await asyncio.sleep(1)
            finally:
                if client and not client.closed:
                    await client.unsubscribe(chan)
                    await redis_factory.close_client(client)

    async def writer(self):
        while True:
            logger.info('redis_rpc_writer: root loop. creating pool')
            try:
                pool = await redis_factory.create_pool()
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
                await asyncio.sleep(1)
            finally:
                logger.info('redis_rpc_writer: finally / closing pool')
                if pool and not pool.closed:
                    await redis_factory.close_pool(pool)

    async def get(self):
        item = await self.queue.get()
        self.queue.task_done()
        return item

    async def request(self, to, method, timeout__=RPC_TIMEOUT, **params):
        """
        Arguments
        timeout__ (int,str) Custom timeout
        """
        mc = MethodCall(dest=to, method=method, source=self.name)
        req_id = str(next(self.id_gen))
        req = Request(mc.tos(), params, request_id=req_id)
        return await self.send(
            req, request_id=req['id'], timeout__=int(timeout__), to=to)

    async def notify(self, to, method, **params):
        mc = MethodCall(dest=to, method=method, source=self.name)
        req = Notification(mc.tos(), **params)
        return await self.send(req, to=to)

    async def put(self, dest, data):
        await self.queue.put((
            dest,
            data,
        ))

    async def send_message(self, request, timeout__=RPC_TIMEOUT, **kwargs):
        to = kwargs['to']
        # Outgoing msg queue
        await self.put(to, request.encode())
        # skip waiting for notification
        if 'request_id' not in kwargs:
            return
        
        req_id = kwargs['request_id']
        # Waiting for response
        try:
            req = self.pending[req_id] = asyncio.Future()
            # await asyncio.wait_for(self.pending[req_id], timeout=self.timeout)
            async with timeout(int(timeout__)) as cm:
                await req
        except asyncio.TimeoutError:
            logger.error(
                'rpc timeout', timeout=timeout__, to=to, req_id=req_id)
        except asyncio.CancelledError:
            logger.warn('Cancelled')
        finally:
            del self.pending[req_id]

        # Retunrning result
        return None if cm.expired else self.process_response(req.result())


__all__ = ['RedisPubSubRPC']
