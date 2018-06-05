from collections import deque, defaultdict, UserDict, namedtuple
from prodict import Prodict


class DotDict(dict):
    def __getattr__(self, attr):
        attr = self[attr]
        return DotDict(attr) if type(attr) == dict else attr

    def __setattr__(self, attr, value):
        self[attr] = value


class MethodRegistration(Prodict):
    service: str
    method: str
    role: str
    options: Prodict
