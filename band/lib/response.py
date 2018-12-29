RESP_PIXEL = 'pixel'
RESP_REDIRECT = 'redirect'
RESP_ERROR = 'error'
RESP_DATA = 'data'


class BandResponse:
    @staticmethod
    def __call__(data):
        return data

    @staticmethod
    def data(data, statusCode=200):
        return {
            'type__': RESP_DATA,
            '_response___type': RESP_DATA,  #TODO: remove it
            'statusCode': statusCode,
            'data': data
        }

    @staticmethod
    def redirect(location, statusCode=302, data={}):
        return {
            'type__': RESP_REDIRECT,
            '_response___type': RESP_REDIRECT,  #TODO: remove it
            'location': location,
            'statusCode': statusCode,
            'data': data
        }

    @staticmethod
    def pixel(data={}):
        return {
            'type__': RESP_PIXEL,
            '_response___type': RESP_PIXEL,  #TODO: remove it
            'data': data
        }

    @staticmethod
    def error(message="", statusCode=500, data={}):
        return {
            'type__': RESP_ERROR,
            '_response___type': RESP_ERROR,  #TODO: remove it
            'errorMessage': message,
            'statusCode': statusCode,
            'data': data,
        }


class BandResponseBase(dict):
    @classmethod
    def from_dict(cls, type__=None, _response___type=None, **data):
        return cls(**data)


class BandResponceError(BandResponseBase):
    def __init__(self, message="", statusCode=500, data={}):
        super().__init__({
            'type__': RESP_ERROR,
            'errorMessage': message,
            'statusCode': statusCode,
            'data': data,
        })


class BandResponceData(BandResponseBase):
    def __init__(self, data, statusCode=200):
        super().__init__({
            'type__': RESP_DATA,
            'statusCode': statusCode,
            'data': data
        })


class BandResponceRedirect(BandResponseBase):
    def __init__(self, location, statusCode=302, data={}):
        super().__init__({
            'type__': RESP_REDIRECT,
            'location': location,
            'statusCode': statusCode,
            'data': data
        })


class BandResponcePixel(BandResponseBase):
    def __init__(self, data={}):
        super().__init__({
            'type__': RESP_PIXEL,
            '_response___type': RESP_PIXEL,  #TODO: remove it
            'data': data
        })


MAP = {
    RESP_DATA: BandResponceData,
    RESP_PIXEL: BandResponcePixel,
    RESP_REDIRECT: BandResponceRedirect,
    RESP_ERROR: BandResponceError
}


def handle_incoming(data):
    if isinstance(data,
                  dict) and ('type__' in data) and (data['type__'] in MAP):
        return MAP[data['type__']].from_dict(**data)
    return data


def error(message="", statusCode=500, data={}):
    return BandResponceError(message, statusCode=statusCode)


def data(data, statusCode=200):
    return BandResponceError(data=data, statusCode=statusCode)


def redirect(location, statusCode=302, data={}):
    return BandResponceError(location, statusCode=statusCode, data=data)


def pixel(data={}):
    return BandResponcePixel(data=data)


__all__ = [
    'error', 'data', 'redirect', 'pixel', 'handle_incoming',
    'BandResponceData', 'BandResponceError', 'BandResponcePixel',
    'BandResponceRedirect'
]
