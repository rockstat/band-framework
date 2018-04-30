from collections import deque, defaultdict, UserDict

class DotDict(dict):
    def __getattr__(self, attr):
        attr = self[attr]
        return DotDict(attr) if type(attr) == dict else attr

    def __setattr__(self, attr, value):
        self[attr] = value


def pick(d, *keys):
    return {k: d[k] for k in keys}

__all__ = ['DotDict', 'pick']

