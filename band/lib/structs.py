from collections import deque, defaultdict, UserDict, namedtuple
from typing import Dict, NamedTuple


class DotDict(dict):
    def __getattr__(self, attr):
        attr = self[attr]
        return DotDict(attr) if type(attr) == dict else attr

    def __setattr__(self, attr, value):
        self[attr] = value

class MethodRegistration(namedtuple('MethodRegistration', 'method role options')):
    __slots__ = ()
    method: str
    role: str
    options: Dict
