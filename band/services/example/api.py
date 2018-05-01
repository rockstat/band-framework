from asyncio import sleep
from band import resp, dome, logger, RESULT_OK


@dome.expose(role=dome.HANDLER)
async def whoisyoudaddy(**params):
    """
    Exposed method
    Communicating with outer world via:
    (service) <--redispubsub--> (kernel) <--http--> (browser)
    """
    return {
        'xxx': '(_._)',
        'params': params
    }


@dome.expose()
async def __status(**params):
    """
    Service status examle with http and rpc
    """
    return {
        'status': RESULT_OK,
        'methods': list(dome.methods.roles_tups)
    }


# @dome.tasks.add
# async def test_background_task():
#     """
#     Background task example
#     """
#     try:
#         i = 0
#         await sleep(3)
#         while True:
#             if i < 5:
#                 print({'task': 'implemented and executed'})
#             # delay between executions
#             i += 1
#             await sleep(3)
#     except Exception:
#         logger.exception('err')