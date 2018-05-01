from jinja2 import Environment, FileSystemLoader, Template
from collections import namedtuple
from dotenv import load_dotenv
from pathlib import Path
import socket
import yaml
import os
from prodict import Prodict

from .log import logger
from .constants import BAND_SERVICE, ENV_DEV, ENV_PROD


def completely_config(dir='.', conf_band='band.yaml', conf_service='service.yaml', env_fn='.env', dev_env_fn='.env.dev'):
    root = Path(os.getcwd())
    load_dotenv(dotenv_path=root/env_fn)
    load_dotenv(dotenv_path=root/dev_env_fn)

    env = os.environ['ENV'] = os.environ.get('ENV', ENV_DEV)
    name = os.environ['NAME'] = os.getenv('NAME', socket.gethostname())
    
    master = name == BAND_SERVICE

    tmplenv = Environment(
        loader=FileSystemLoader(str(root))
    )
    tmpl = tmplenv.get_template(conf_band if master else conf_service)
    data = tmpl.render(**os.environ)
    data = yaml.load(data)
    data.update({
        'name': name,
        'master': master,
        'env': env
    })
    return Prodict.from_dict(data)

settings = completely_config()

logger.info('pid: %s', os.getpid())
logger.info('cwd:%s', os.getcwd())
logger.info('settings: %s', settings)

__all__ = ['completely_config', 'settings']
