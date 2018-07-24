from aiohttp.web import json_response as _json_response, middleware, HTTPException, Response
import time
from band import logger

def json_response(result, status=200, request=None):
    return _json_response(result, headers=cors_headers(request=request))


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
    return say_cors_yes(
        request) if request.method == 'OPTIONS' else await handler(request)


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
