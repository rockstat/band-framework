from jinja2 import Environment, FileSystemLoader, Template
import collections
import os
import yaml
from path import Path
from .env import environ
from ..log import logger

def reader(fn):
    logger.debug('loading', f=fn)
    p = Path(fn)
    try:
        tmplenv = Environment(loader=FileSystemLoader(p.dirname()))
        tmpl = tmplenv.get_template(str(p.basename()))
        part = tmpl.render(**environ)
        data = yaml.load(part)
        return data
        
    except Exception:
        logger.exception('config')

