"""
Common helpers collection
"""
from typing import Dict

from ..config import environ


def envIsYes(name, default='', environ=environ):
    return environ.get(name, default).lower() in ("yes", "true", "t", "1")


def none_none(dick: Dict):
    dict.__class__({k: v for k, v in dick.items() if v is not None})
