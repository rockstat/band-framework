from jinja2 import Environment, FileSystemLoader, Template
from collections import namedtuple
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint
import socket
import yaml
import os
import sys
from prodict import Prodict

from .log import logger
from .constants import BAND_SERVICE, ENV_DEV, ENV_PROD


def completely_config(dir='.',
                      conf='config.yaml',
                      env_fn='.env',
                      env_local_fn='.env.local'):

    root = Path(os.getcwd())
    load_dotenv(dotenv_path=root / env_fn)
    load_dotenv(dotenv_path=root / env_local_fn)

    env = os.environ['ENV'] = os.environ.get('ENV', ENV_DEV)
    name_env = os.environ['NAME'] = os.getenv('NAME', socket.gethostname())
    tmplenv = Environment(loader=FileSystemLoader(str(root)))
    tmpl = tmplenv.get_template(conf)
    data = tmpl.render(**os.environ)
    data = yaml.load(data)
    data.update({
        # use pre configured or detected service name
        'name': data.get('name', name_env),
        'env': env
    })
    return Prodict.from_dict(data)


try:
    settings = completely_config()
except Exception:
    logger.exception('config')

logger.info('pid: %s', os.getpid())
logger.info('cwd:%s', os.getcwd())
logger.info('settings: %s', settings)

__all__ = ['completely_config', 'settings']
