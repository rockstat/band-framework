from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import collections
import os
from os.path import dirname, basename

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


from .env import environ
from ..log import logger

def reader(fn):
    logger.debug('loading', f=fn)
    try:
        tmplenv = Environment(loader=FileSystemLoader(dirname(fn)))
        tmpl = tmplenv.get_template(str(basename(fn)))
        part = tmpl.render(**environ)
        data = load(part, Loader=Loader)
        return data
    except TemplateNotFound:
        logger.warn('Template not found', file=fn)
    except Exception:
        logger.exception('config')

