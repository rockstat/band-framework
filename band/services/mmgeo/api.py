import subprocess
import os.path
import maxminddb
from band import dome, logger, RESULT_INTERNAL_ERROR, RESULT_NOT_LOADED_YET


class State(dict):
    pass


state = State()
DB_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
PATH = './data'
ARCH = f'{PATH}/mmdb.zip'
TRG = f'{PATH}/GeoLite2-City.mmdb'
CMD = f'mkdir -p {PATH} && wget -q -O {ARCH} {DB_URL} && tar -zxf {ARCH} --strip=1 -C {PATH} && rm -rf {ARCH}'

"""
Library docs: https://github.com/maxmind/MaxMind-DB-Reader-python

For better performance you cat install C version of lib
https://github.com/maxmind/libmaxminddb

"""


@dome.tasks.add
async def download_db():
    try:
        if not os.path.isfile(TRG):
            logger.info('downloading database. cmd: %s', CMD)
            out = subprocess.call(CMD, shell=True)
            logger.info('download result %s', out)
        state['geodata'] = maxminddb.open_database(TRG)
    except Exception:
        logger.exception('download err')


@dome.expose(role=dome.HANDLER)
async def get(ip, **params):
    try:
        if 'geodata' in state:
            location = state['geodata'].get(ip)
            return location
        return {'result': RESULT_NOT_LOADED_YET}
    except Exception:
        logger.exception('get ip err')
    return {'result': RESULT_INTERNAL_ERROR}
