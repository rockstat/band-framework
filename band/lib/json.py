import orjson
import json


def json_def(obj):
    if isinstance(obj, dict):
        return dict(obj)
