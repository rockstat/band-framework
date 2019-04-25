from typing import NamedTuple, Dict

from ..lib.json import json_def, json_dumps, json_loads

RESP_PIXEL = 'pixel'
RESP_REDIRECT = 'redirect'
RESP_ERROR = 'error'
RESP_DATA = 'data'


class BaseBandResponse(dict):
    type__: str = None

    def to_json(self):
        return json_dumps(self._asdict())

    def is_redirect(self):
        return self.type__ == RESP_REDIRECT

    def is_data(self):
        return self.type__ == RESP_DATA

    def is_pixel(self):
        return self.type__ == RESP_PIXEL

    def is_error(self):
        return self.type__ == RESP_ERROR

    @property
    def type(self):
        return self.type__

    def __getattr__(self, key):
        return self.get(key)


class BandResponceError(BaseBandResponse):
    errorMessage: str
    statusCode: int
    data: Dict
    type__: str = RESP_ERROR

    def __init__(self, errorMessage='Unknown error', statusCode=500, data={}):
        super().__init__(data)
        self.type__ = self.type__
        self.errorMessage = errorMessage
        self.statusCode = statusCode

    @property
    def error_message(self):
        return self.errorMessage

    @property
    def status_code(self):
        return self.statusCode

    def __str__(self):
        return f'Error: {self.errorMessage} ({self.statusCode})'

    def _asdict(self):
        return {
            'type__': self.type__,
            'statusCode': self.statusCode,
            'errorMessage': self.errorMessage,
            'data': self
        }

class BandResponceData(BaseBandResponse):
    data: Dict
    statusCode: int
    type__: str = RESP_DATA

    def __init__(self, data, statusCode=200):
        super().__init__(data)
        self.type__ = self.type__
        self.statusCode = statusCode

    def __str__(self):
        return f'Data: {self}'

    def status_code(self):
        return self['statusCode']

    def _asdict(self):
        return {
            'type__': self.type__,
            'statusCode': self.statusCode,
            'data': self
        }


class BandResponceRedirect(BaseBandResponse):
    location: str
    statusCode: int
    data: Dict
    type__: str = RESP_REDIRECT

    def __init__(self, location, data={}, statusCode=302):
        super().__init__(data)
        self.location = location
        self.statusCode = statusCode

    def status_code(self):
        return self.statusCode

    def __str__(self):
        return f'Redirect: {self.location}'

    def _asdict(self):
        return {
            'type__': self.type__,
            'location': self.location,
            'statusCode': self.statusCode,
            'data': self
        }

class BandResponcePixel(BaseBandResponse):
    
    data: Dict = {}
    type__: str = RESP_PIXEL

    def __init__(self, data={}):
        super().__init__(data)

    def __str__(self):
        return 'Pixel'

    def _asdict(self):
        return {
            'type__': self.type__,
            'data': self
        }


MAP = {
    RESP_DATA: BandResponceData,
    RESP_PIXEL: BandResponcePixel,
    RESP_REDIRECT: BandResponceRedirect,
    RESP_ERROR: BandResponceError
}


def create_response(data):
    if isinstance(data, dict):
        type__ = data.pop('type__', None)
        if type__ and (type__ in MAP):
            # for data return only data
            if type__ == RESP_DATA:
                return data.get('data')
            # other typed responses
            return MAP[type__](**data)
    return data


def error(errorMessage="", statusCode=500, data={}):
    return BandResponceError(errorMessage, statusCode=statusCode, data=data)


def data(data, statusCode=200):
    return BandResponceData(data, statusCode=statusCode)


def redirect(location, statusCode=302, data={}):
    return BandResponceRedirect(location, statusCode=statusCode, data=data)


def pixel(data={}):
    return BandResponcePixel(data=data)


__all__ = [
    'error', 'data', 'redirect', 'pixel', 'create_response',
    'BandResponceData', 'BandResponceError', 'BandResponcePixel',
    'BandResponceRedirect', 'BaseBandResponse'
]
