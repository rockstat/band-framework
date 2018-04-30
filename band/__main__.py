# /usr/bin/env python
import os

from .lib import logger
from .band_async import run_server
from .config import load_config

logger.info('Working directory %s', os.getcwd())
conf = load_config()

def main():
    run_server(**conf)


if __name__ == '__main__':
    main()
