import os
from os import environ
import socket
from dotenv import load_dotenv
from pathlib import Path

ENV_DEV = 'development'
ENV_PROD = 'production'

env_fn = '.env'
env_local_fn = '.env.local'

root = Path(os.getcwd())
load_dotenv(dotenv_path=root / env_local_fn)
load_dotenv(dotenv_path=root / env_fn)

env = environ['ENV'] = environ.get('ENV', ENV_DEV)
name_env = environ['NAME'] = environ.get('NAME', socket.gethostname())
