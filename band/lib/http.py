import time
import ujson
from aiohttp.web import (json_response as _json_response,
                         middleware, HTTPException, Response, RouteTableDef, RouteDef)

from band import logger, error


def json_response(result, status=200, request=None):
    return _json_response(result, status=status, headers=cors_headers(request=request))


async def request_handler(request, handler):
    # get query
    query = dict(**request.query)
    # url params
    if request.method == 'POST':
        if request.content_type == 'application/json':
            raw = await request.text()
            if raw:
                query.update(ujson.loads(raw))
        else:
            post = await request.post()
            query.update(post)
    # url params
    query.update(request.match_info)
    try:
        result = await handler(**query)
        return json_response(result, request=request)
    except Exception:
        logger.exception("Exc")
        return error("Error while executing controller")
    


def add_http_handler(handler, path, **kwargs):
    logger.info('Adding route', path=path)

    async def wrapper(request):
        return await request_handler(request, handler)

    return [
        RouteDef('GET', path, wrapper, kwargs),
        RouteDef('POST', path, wrapper, kwargs)
    ]


def say_cors_yes(request=None):
    return Response(headers=cors_headers(request=request))


def cors_headers(request):
    origin = request.headers.get('ORIGIN', '*')
    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'X-Requested-With,Content-Type'
    }


@middleware
async def naive_cors_middleware(request, handler):
    """
    Simple CORS middleware to access api from dashboard
    """
    if request.method == 'OPTIONS':
        return say_cors_yes(request)
    else:
        return await handler(request)


@middleware
async def error_middleware(request, handler):

    try:
        response = await handler(request)
        return response

    except HTTPException as ex:
        return _json_response({'error': ex.reason}, status=ex.status)

    except Exception as ex:
        logger.exception('error middleware ex')
        return _json_response({'error': 'Internal server error'}, status=500)

    return error_middleware


@middleware
async def json_middleware(request, handler):
    status_code = 200
    try:
        response = await handler(request)
    # except web.HTTPException as ex:
    #     if ex.status != 404:
    #         raise
    #     message = ex.reason
    except Exception as e:
        logge
        response = {'error': str(e)}
        status_code = 500

    return _json_response(response, headers=cors_headers(request=request))


# headers = dict()
# headers['Access-Control-Allow-Origin'] = '*'
# headers['Access-Control-Allow-Credentials'] = 'true'
# headers['Access-Control-Allow-Headers'] = 'X-Requested-With,Content-Type'

__all__ = [
    'json_response', 'say_cors_yes', 'json_middleware',
    'naive_cors_middleware', 'error_middleware'
]
