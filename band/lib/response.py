from ..constants import RESP_META_KEY, RESP_TYPE_KEY

RESP_PIXEL = 'pixel'
RESP_REDIRECT = 'redirect'
RESP_ERROR = 'error'


class BandResponse:

    def __call__(self, data):
        return data

    def redirect(self, location, statusCode=302, data={}):
        return {
            RESP_TYPE_KEY: RESP_REDIRECT,
            'location': location,
            'statusCode': statusCode,
            'data': data
        }

    def pixel(self, data={}):
        return {
            RESP_TYPE_KEY: RESP_PIXEL,
            'data': data
        }

    def error(self, message="", statusCode=500, data={}):
        return {
            RESP_TYPE_KEY: RESP_ERROR,
            'message': message,
            'statusCode': statusCode,
            'data': data,
        }


__all__ = ['BandResponse']
