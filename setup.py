__VERSION__ = '0.3.3'

from setuptools import setup, find_packages

setup(
    name='band',
    version=__VERSION__,
    author='Dmitry Rodin',
    author_email='madiedinro@gmail.com',
    license='MIT',
    description='Python microservices for Rockstat analytics plaform',
    long_description="""
About
---
Orchestranion module start services in docker containers, examine and send configuraton to the frontier service.
Includes microserivice framework for easy develop simple services and easy expose by https through frontier.
More at project documentation
    """,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://github.com/rockstat/band',
    include_package_data=True,
    install_requires=[
        'pyyaml', 'inflection', 'jinja2', 'coloredlogs', 'asyncio', 'uvloop',
        'aiohttp', 'aioredis', 'aiojobs', 'aiodocker', 'aiofiles', 'async_lru',
        'jsonrpcserver', 'jsonrpcclient==2.6.0', 'requests', 'python-dotenv',
        'prodict', 'ujson', 'asimplech>=0.1.7'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={  # Optional
        'Homepage': 'https://rstat.org',
        'Docs': 'https://rstat.org/docs'
    })
