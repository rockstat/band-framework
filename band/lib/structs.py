from collections import deque, defaultdict, UserDict, namedtuple

class DotDict(dict):
    def __getattr__(self, attr):
        attr = self[attr]
        return DotDict(attr) if type(attr) == dict else attr

    def __setattr__(self, attr, value):
        self[attr] = value

class MethodRegistration(namedtuple('MethodRegistration', ['service', 'method', 'role', 'options'])):
    __slots__ = ()
    def to_dict(self):
        return {
            'service': self.service,
            'method': self.method,
            'role': self.role,
            'options': self.options
        }


__all__ = ['DotDict', 'MethodRegistration']
