from aiohttp.web import json_response
import time


# headers = dict()
# headers['Access-Control-Allow-Origin'] = '*'
# headers['Access-Control-Allow-Credentials'] = 'true'
# headers['Access-Control-Allow-Headers'] = 'X-Requested-With,Content-Type'
def cors_headers(request):
    origin = request.headers.get('ORIGIN', '*')
    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'X-Requested-With,Content-Type'
    }


def resp(result, status=200, request=None):
    # data = {'result': result, 'ts': round(time.time() * 1000)}
    return json_response(result, headers=cors_headers(request=request))


def say_cors_yes(request=None):
    return web.Response(headers=cors_headers(request=request))


__all__ = ['resp', 'say_cors_yes']
