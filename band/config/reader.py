from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import collections
import os
import yaml
from os.path import dirname, basename
from .env import environ
from ..log import logger

def reader(fn):
    logger.debug('loading', f=fn)
    try:
        tmplenv = Environment(loader=FileSystemLoader(dirname(fn)))
        tmpl = tmplenv.get_template(str(basename(fn)))
        part = tmpl.render(**environ)
        data = yaml.load(part)
        return data
    except TemplateNotFound:
        logger.warn('Template not found', file=fn)
    except Exception:
        logger.exception('config')

