# /usr/bin/env python
from dotenv import load_dotenv
from pathlib import Path
import os
from .band_async import run_server


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

print(os.getcwd())

host = os.getenv('HOST', '127.0.0.1')
port = os.getenv('PORT', 10000)
band = os.getenv('BAND', 'http://127.0.0.1:10000')
cbind = os.getenv('CONTAINERS_BIND', 'http://127.0.0.1:10000')
redis_dsn = os.getenv('REDIS_DSN', 'redis://127.0.0.1')
ipath = os.getenv('IMAGES_PATH', '../images')


def main():
    run_server(host=host, port=port, band_url=band, cbind=cbind,
               redis_dsn=redis_dsn, images_path=ipath)


if __name__ == '__main__':
    main()
