import time
import uvloop
import asyncio
from aiohttp import web
from jsonrpcserver import methods

from .redis_rpc import RedisClientAsync
from .dock import Dock
from .lib import *


def makeresp(result, status=200):
    data = {'result': result, 'ts': round(time.time()*1000)}
    return web.json_response(data)


def setup_routes(app, dock, rpc):
    routes = web.RouteTableDef()

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
        result = await rpc.request(KERNEL_SERVICE, 'status', **{'format': 'short'})
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


async def startup_tasks(app):
    app['redis_rpc_writer'] = app.loop.create_task(app['rpc'].writer(app))
    app['redis_rpc_reader'] = app.loop.create_task(app['rpc'].reader(app))


async def cleanup_tasks(app):
    for key in ['redis_rpc_reader', 'redis_rpc_writer']:
        app[key].cancel()
        await app[key]


def run_server(http_host, http_port, bind_addr, redis_dsn, band_url, images_path):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    dock = Dock(images_path=images_path,
                bind_addr=bind_addr, band_url=band_url)

    app = web.Application(loop=loop, logger=logger)
    rpc = RedisClientAsync(service=BAND_SERVICE, redis_dsn=redis_dsn)

    routes = setup_routes(app, dock=dock, rpc=rpc)
    app.router.add_routes(routes)

    for key, val in [('rpc', rpc), ('dock', dock)]:
        app[key] = val

    app.on_startup.append(startup_tasks)
    app.on_shutdown.append(cleanup_tasks)

    web.run_app(app, host=http_host,
                port=http_port, handle_signals=True)
