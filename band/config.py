from jinja2 import Environment, FileSystemLoader, Template
from dotenv import load_dotenv
from pathlib import Path
from box import Box
import yaml
import os


def load_config(dir='.', conf_fn='config.yaml', env_fn='.env'):
    root = Path(dir)
    load_dotenv(dotenv_path=root/env_fn)

    env = Environment(
        loader=FileSystemLoader(str(root))
    )
    tmpl = env.get_template(conf_fn)
    data = tmpl.render(**os.environ)
    return Box(yaml.load(data))


