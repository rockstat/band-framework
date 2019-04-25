# import orjson
import json
import ujson


def json_def(obj):
    if isinstance(obj, dict):
        return dict(obj)


def json_dumps(data):
    return ujson.dumps(data, ensure_ascii=False)


def json_loads(data):
    return ujson.loads(data)

