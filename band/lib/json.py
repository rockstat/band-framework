# import orjson
import json
import ujson


def json_def(obj):
    if isinstance(obj, dict):
        return dict(obj)


def json_dumps(data, **kwargs):
    # kwargs.pop('default', None)
    # kwargs['ensure_ascii'] = False
    return ujson.dumps(data, ensure_ascii=False)


def json_loads(data):
    return ujson.loads(data)

