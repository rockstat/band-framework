from jinja2 import Environment, FileSystemLoader, Template
import collections
import os
from pprint import pprint
from prodict import Prodict as pdict

from .env import env, name_env, environ, ENVS
from .reader import reader
from ..log import logger


DEFAULT_FILES = ['config.yaml' ,'config.yml', 'custom.yaml', 'custom.yml']

root = os.getcwd()

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
    data = reader(f'{root}/{fn}')
    if data:
        update(config, data)



config.update({
    'name': config.get('name', name_env)
})

# Support for env subconfigs
env_subsection = config.pop(env, {})
config.update(env_subsection)


settings = pdict.from_dict(config)

__all__ = ['settings']
