import time
import uvloop
import asyncio
from aiohttp import web

from . import register
from .redis_rpc import RedisClientAsync
from .dock import Dock
from .lib import logger, RESULT_OK, RESULT_PONG, BAND_SERVICE, KERNEL_SERVICE


def resp(result, status=200):
    data = {'result': result, 'ts': round(time.time()*1000)}
    return web.json_response(data)


def setup_routes(app, dock, rpc):
    routes = web.RouteTableDef()

    # Registering new service
    @register.methods.add
    async def service_register(**kwargs):
        # return dock.run_container(name, data)
        print(kwargs)
        return True

    # Creating and running new service
    @register.methods.add
    async def service_run(name, data):
        return dock.run_container(name, data)

    # Ping request
    @register.methods.add
    async def service_ping(name):
        dock.ping(name)

    # Ask service status
    @register.methods.add
    async def ask_status(name):
        return await rpc.request(name, 'status')

    ########## HTTP ROUTES

    @register.routes.get('/')
    async def http_index(request):
        return resp(RESULT_OK)

    @routes.post('/register')
    async def http_service_register(request):
        data = await request.post()
        c = await service_register(data)
        return resp(c)

    @routes.post('/run/{name}')
    async def http_service_run(request):
        data = await request.post()
        name = request.match_info['name']
        c = await service_run(name, data)
        return resp(c)

    @routes.get('/ping/{name}')
    async def http_ping(request):
        name = request.match_info['name']
        await service_ping(name)
        return resp(RESULT_PONG)

    @routes.get('/ask_status/{name}')
    async def http_ask_status(request):
        result = await ask_status(request.match_info['name'])
        return resp(result)

    # Unregister service request
    @routes.get('/unload/{name}')
    async def unload(request):
        name = request.match_info['name']
        res = dock.remove_container(name)
        return resp(res)

    @routes.get('/list')
    async def containers(request):
        return resp(dock.containers_list())

    @routes.get('/stop/{name}')
    async def stop(request):
        name = request.match_info['name']
        return resp(dock.stop_container(name))

    return routes


async def startup_tasks(app):
    app['redis_rpc_writer'] = app.loop.create_task(app['rpc'].writer(app))
    app['redis_rpc_reader'] = app.loop.create_task(app['rpc'].reader(app))


async def cleanup_tasks(app):
    for key in ['redis_rpc_reader', 'redis_rpc_writer']:
        app[key].cancel()
        await app[key]


def run_server(http_host, http_port, bind_addr, redis_dsn, band_url, images_path, service):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    dock = Dock(images_path=images_path, redis_dsn=redis_dsn,
                bind_addr=bind_addr, band_url=band_url)

    app = web.Application(loop=loop, logger=logger)
    rpc = RedisClientAsync(service=service, redis_dsn=redis_dsn)

    routes = setup_routes(app, dock=dock, rpc=rpc)
    app.router.add_routes(routes)

    for key, val in [('rpc', rpc), ('dock', dock)]:
        app[key] = val

    app.on_startup.append(startup_tasks)
    app.on_shutdown.append(cleanup_tasks)

    web.run_app(app, host=http_host,
                port=http_port, handle_signals=True)
