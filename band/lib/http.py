from aiohttp import web
import time

def resp(result, status=200):
    data = {'result': result, 'ts': round(time.time()*1000)}
    return web.json_response(data)


__all__ = ['resp']

