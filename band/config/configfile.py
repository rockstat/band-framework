from jinja2 import Environment, FileSystemLoader, Template
import collections

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

CONFIG_FILES = ['config.yaml', 'custom.yml']


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

try:
    root = Path(os.getcwd())
    config = {}
    tmplenv = Environment(loader=FileSystemLoader(str(root)))
    for fn in CONFIG_FILES:
        if os.path.exists(fn):
            tmpl = tmplenv.get_template(fn)
            part = tmpl.render(**environ)
            data = yaml.load(part)
            update(config, data)
    
    
    config.update({
        # use pre configured or detected service name
        'name': data.get('name', name_env),
        'env': env,
        '_pid': os.getpid(),
        '_cwd': os.getcwd()
    })
    settings = Prodict.from_dict(data)
except Exception:
    logger.exception('config')


__all__ = ['settings']
