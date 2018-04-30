from jinja2 import Environment, FileSystemLoader, Template
from dotenv import load_dotenv
from pathlib import Path
import yaml
import os

from . import logger, DotDict

ENV_DEV = 'development'
ENV_PROD = 'production'

def completely_config(dir='.', conf_fn='band.yaml', env_fn='.env', dev_env_fn='.env.dev'):
    logger.info('pid: %s; cwd:%s', os.getpid(), os.getcwd())

    root = Path(os.getcwd())
    load_dotenv(dotenv_path=root/env_fn)

    ENV = os.environ['ENV'] = os.environ.get('ENV', ENV_DEV)
    if ENV == ENV_DEV:
        load_dotenv(dotenv_path=root/dev_env_fn)
    
    env = Environment(
        loader=FileSystemLoader(str(root))
    )

    tmpl = env.get_template(conf_fn)
    data = tmpl.render(**os.environ)
    return DotDict(yaml.load(data))

__all__ = ['completely_config', 'ENV_DEV', 'ENV_PROD']
