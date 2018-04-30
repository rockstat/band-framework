from asyncio import sleep
from band import resp, dome, RESULT_OK


@dome.routes.get('/test_api')
async def my_method(request):
    """
    HTTP exposing.
    Currently not exposed outside
    (service) <--http--> (xxx)
    """
    data = {
        'answer': 'api working!'
    }
    return resp(data)


@dome.tasks.add
async def test_background_task():
    """
    Background task example
    """
    i = 0
    await sleep(3)
    while True:
        if i % 100 == 0:
            print({'task': 'implemented and executed'})
        # delay between executions
        i += 1
        await sleep(3)


@dome.methods.add(role='handler')
async def whoisyoudaddy(**kwargs):
    """
    Exposed method
    Communicating with outer world via:
    (service) <--redispubsub--> (kernel) <--http--> (browser)
    """
    return {
        'xxx': '(_._)',
        'params': kwargs
    }


@dome.methods.add
def __status():
    """
    Service status examle with http and rpc
    """
    return {'status': RESULT_OK, 'methods': list(dome.methods.roles_tups)}


@dome.routes.get('/__status')
async def http_status(request):
    """
    HTTP differs by params, however it can be unified
    Currently HTTP dont't exposing outside! Only for internal usage
    """
    return resp(__status())
