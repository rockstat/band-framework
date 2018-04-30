from asyncio import sleep

from ..lib import resp, RESULT_OK, RESULT_PONG, BAND_SERVICE, KERNEL_SERVICE
from .. import dome

# Registering new service
@dome.methods.add
async def service_register(**kwargs):
    print(kwargs)
    return True

# Creating and running new service
@dome.methods.add
async def service_run(name, data):
    return dock.run_container(name, data)

# Ping request
@dome.methods.add
async def service_ping(name):
    dock.ping(name)

# Ask service status
@dome.methods.add
async def ask_status(name):
    return await rpc.request(name, 'status')

########## HTTP ROUTES

@dome.routes.get('/')
async def http_index(request):
    return resp(RESULT_OK)

@dome.post('/register')
async def http_service_register(request):
    data = await request.post()
    c = await service_register(data)
    return resp(c)

@dome.post('/run/{name}')
async def http_service_run(request):
    data = await request.post()
    name = request.match_info['name']
    c = await service_run(name, data)
    return resp(c)

@dome.get('/ping/{name}')
async def http_ping(request):
    name = request.match_info['name']
    await service_ping(name)
    return resp(RESULT_PONG)

@dome.get('/ask_status/{name}')
async def http_ask_status(request):
    result = await ask_status(request.match_info['name'])
    return resp(result)

# Unregister service request
@dome.get('/unload/{name}')
async def unload(request):
    name = request.match_info['name']
    res = dock.remove_container(name)
    return resp(res)

@dome.get('/list')
async def containers(request):
    return resp(dock.containers_list())

@dome.get('/stop/{name}')
async def stop(request):
    name = request.match_info['name']
    return resp(dock.stop_container(name))

