from jinja2 import Environment, FileSystemLoader, Template
import collections

import os
from path import Path
from pprint import pprint
import yaml
from prodict import Prodict as pdict

from ..log import logger
from .env import env, name_env, environ
from .reader import reader

DEFAULT_FILES = ['config.yaml', 'custom.yml']

root = Path(os.getcwd())

config = {
    'env': env,
    '_pid': os.getpid(),
    '_cwd': os.getcwd()
}

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

for fn in DEFAULT_FILES:
    data = reader(root / fn)
    if data:
        update(config, data)

config.update({
    'name': config.get('name', name_env)
})
settings = pdict.from_dict(config)

__all__ = ['settings']
