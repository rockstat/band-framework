"""
Common helpers collection
"""
from typing import Dict

from ..config import environ


def env_is_true(name, default='', environ=environ):
    return environ.get(name, default).lower() in ("yes", "true", "t", "1")


def without_none(dick: dict) -> dict: 
    return {k: v for k, v in dick.items() if v is not None}
