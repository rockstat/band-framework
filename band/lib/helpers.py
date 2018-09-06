"""
Common helpers collection
"""

from ..config import environ


def envIsYes(name, default='', environ=environ):
    return environ.get(name, default).lower() in ("yes", "true", "t", "1")
