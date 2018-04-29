import configparser
import os

config = configparser.ConfigParser()
config.read('../params.ini')

listen = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('PORT', '10000')

DS = 'DEFAULT'

def set_options(**kwargs):
    for k, v in kwargs.items():
        config.set(DS, k, v)

set_options(listen=listen, port=port)

def option(name, section=DS):
    if name in config.sections():
        return config[name]
    return config[section].get(name)

