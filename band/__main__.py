# /usr/bin/env python
from dotenv import load_dotenv
from pathlib import Path
import os
from jinja2 import Environment, FileSystemLoader, Template
import yaml
from box import Box

from .lib import logger
from .band_async import run_server

logger.info('Working directory %s', os.getcwd())


def load_config(dir='.', conf_fn='config.yaml', env_fn='.env'):
    root = Path(dir)
    load_dotenv(dotenv_path=root/env_fn)

    env = Environment(
        loader=FileSystemLoader(str(root))
    )
    tmpl = env.get_template(conf_fn)
    data = tmpl.render(**os.environ)
    return Box(yaml.load(data))


conf = load_config()
logger.debug('config: %s')
# pprint(conf)

def main():
    run_server(**conf)


if __name__ == '__main__':
    main()
