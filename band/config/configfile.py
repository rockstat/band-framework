from jinja2 import Environment, FileSystemLoader, Template
from collections import namedtuple
import os
from pathlib import Path
from pprint import pprint
import socket
import yaml
import sys
from prodict import Prodict

from ..log import logger
from ..constants import DIRECTOR_SERVICE
from .env import ENV_DEV, ENV_PROD, env, name_env, environ

CONFIG_FILE = 'config.yaml'
CONFIG_DIR = '.'

try:
    root = Path(os.getcwd())
    tmplenv = Environment(loader=FileSystemLoader(str(root)))
    tmpl = tmplenv.get_template(CONFIG_FILE)
    config = tmpl.render(**environ)
    data = yaml.load(config)
    data.update({
        # use pre configured or detected service name
        'name': data.get('name', name_env),
        'env': env
    })
    settings = Prodict.from_dict(data)
except Exception:
    logger.exception('config')

logger.info('pid: %s', os.getpid())
logger.info('cwd:%s', os.getcwd())
logger.info('settings: %s', settings)

__all__ = ['completely_config', 'settings']
