import os
import sys
import time
import signal
import ssl
import uvloop
import asyncio
import aioredis
from aiohttp import web

from jsonrpcserver.aio import methods
import jsonrpcserver
import ujson

from .pub_queue import PubQueue
from .dock import Dock
from .lib import logger, DotDict


# userful links

# http://aioredis.readthedocs.io/en/v1.1.0/start.html#pub-sub-mode
# https://docs.aiohttp.org/en/stable/web_advanced.html#background-tasks
# https://xinhuang.github.io/posts/2017-07-31-common-mistakes-using-python3-asyncio.html
# https://github.com/aio-libs/aioredis/blob/master/examples/pubsub.py
# https://github.com/pengutronix/aiohttp-json-rpc

BAND_SERVICE = 'band'
KERNEL_SERVICE = 'kernel'

# Json RPC
RESULT_OPERATING = 'operating'
RESULT_PONG = 'pong'
RESULT_OK = 'ok'
RESULT_NOT_FOUND = 'not found'
RESULT_INTERNAL_ERROR = 'internal server error'


def makeresp(result, status=200):
    data = {'result': result, 'ts': round(time.time()*1000)}
    return web.json_response(data)


def setup_routes(app, dock):
    routes = web.RouteTableDef()
    pub_queue = app['pub_queue']

    @routes.get('/')
    async def http_index(request):
        return makeresp(RESULT_OK)

    # Registering new service
    @methods.add
    async def service_register(name, data):
        return dock.run_container(name, data)

    @routes.post('/register/{name}')
    async def http_register(request):
        data = await request.post()
        name = request.match_info['name']
        c = await service_register(name, data)
        return makeresp(c)

    # Ping request
    @methods.add
    async def service_ping(name):
        dock.ping(name)

    @routes.get('/ping/{name}')
    async def http_ping(request):
        name = request.match_info['name']
        await service_ping(name)
        return makeresp(RESULT_PONG)

    # Ask kernel status
    @routes.get('/kernel_status')
    async def http_kernel_status(request):
        result = await pub_queue.request(KERNEL_SERVICE, 'status', {'format': 'short'})
        return makeresp(result)

    # Unregister service request
    @routes.get('/unregister/{name}')
    async def unregister(request):
        name = request.match_info['name']
        dock.remove_container(name)

    @routes.get('/list')
    async def containers(request):
        return makeresp(dock.containers_list())

    @routes.get('/stop/{name}')
    async def stop(request):
        name = request.match_info['name']
        return makeresp(dock.stop_container(name))

    return routes


async def redis_rpc_writer(app):
    try:
        pub_queue = app['pub_queue']
        pub = await aioredis.create_redis_pool('redis://localhost', loop=app.loop)
        logger.info('redis_rpc_writer: entering loop')
        while True:
            service, msg = await pub_queue.get()
            try:
                await pub.publish(service, msg)
            except Exception as error:
                logger.error('redis_rpc_writer: error %s', error)
                print(error)

    except asyncio.CancelledError:
        logger.info('redis_rpc_writer: cancelled')
        pass
    finally:
        await pub.quit()


async def redis_rpc_reader(app):

    while True:
        try:
            pub_queue = app['pub_queue']
            sub = await aioredis.create_redis('redis://localhost', loop=app.loop)
            ch, *_ = await sub.subscribe('band')
            logger.debug('redis_rpc_reader: entering loop')
            while await ch.wait_message():
                msg = await ch.get(encoding='utf-8')
                try:
                    msg = ujson.loads(msg)
                    if 'params' in msg and 'id' in msg:
                        to, method, sender = msg['method'].split(':')
                        if to == BAND_SERVICE:
                            msg['method'] = method
                            response = await methods.dispatch(msg)
                            if not response.is_notification:
                                await pub_queue.put(sender, ujson.dumps(response))
                    if 'result' in msg:
                        await pub_queue.dispatch(msg)
                except Exception as error:
                    logger.error('json parse error %s', error)

        except aioredis.ConnectionClosedError:
            logger.debug('redis_rpc_reader: conn closed')
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.debug('redis_rpc_reader: cancelled')
            break
        except Exception as error:
            logger.error('redis_rpc_reader: error %s', error)
            await asyncio.sleep(1)
        finally:
            if not sub.closed:
                await sub.unsubscribe(ch.name)
                await sub.quit()


async def append_redis_tasks(app):
    app['redis_rpc_writer'] = app.loop.create_task(redis_rpc_writer(app))
    app['redis_rpc_reader'] = app.loop.create_task(redis_rpc_reader(app))


async def cleanup_redis_tasks(app):
    app['redis_rpc_writer'].cancel()
    await app['redis_rpc_writer']
    app['redis_rpc_reader'].cancel()
    await app['redis_rpc_reader']


def run_server(host, port, cbind, redis_dsn, band_url, images_path):

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    # Docker wrapper
    dock = Dock(images_path=images_path,
                cbind=cbind, band_url=band_url)

    app = web.Application(loop=loop, logger=logger)
    app['pub_queue'] = PubQueue(service=BAND_SERVICE)

    routes = setup_routes(app, dock)
    app.router.add_routes(routes)
    app.on_startup.append(append_redis_tasks)
    app.on_shutdown.append(cleanup_redis_tasks)

    web.run_app(app, host=host,
                port=port, handle_signals=True)
