import time
import ujson
import asyncio
from aiohttp.web import (json_response as _json_response, middleware,
                         HTTPException, Response, RouteTableDef, RouteDef, StreamResponse)
from jsonrpcclient.exceptions import ReceivedErrorResponse
from band import logger, response
import types

def json_response(result, status=200, request=None):
    return _json_response(
        body=ujson.dumps(result, ensure_ascii=False),
        status=status,
        headers=cors_headers(request=request))


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
        # Handling stream responses
        if isinstance(result, types.AsyncGeneratorType):
            try:
                stream = StreamResponse()
                await stream.prepare(request)
                async for block in result:
                    await stream.write(block)
                await stream.write_eof()
                return stream
            # Halt handling
            except asyncio.CancelledError:
                logger.warn('halted response')
            return stream
        # regilar response
        else:
            return json_response(result, request=request)
    except ReceivedErrorResponse as e:
        return json_response(response.error(e.message), request=request)
    except Exception as e:
        logger.exception("exc")
        return json_response(response.error(str(e)), request=request)


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
        logger.exception('error middleware http ex')
        return json_response({
            'error': ex.reason
        },
                             status=ex.status,
                             request=request)

    except Exception as ex:
        logger.exception('error middleware ex')
        return json_response({
            'error': 'Internal server error'
        },
                             status=500,
                             request=request)

    return error_middleware


__all__ = [
    'json_response', 'say_cors_yes', 'naive_cors_middleware',
    'error_middleware'
]
