__VERSION__ = '0.17.3'

from setuptools import setup, find_packages

setup(
    name='band',
    version='0.17.3',
    author='Dmitry Rodin',
    author_email='madiedinro@gmail.com',
    license='MIT',
    description='Python microservices for Rockstat analytics plaform',
    long_description="""
About
---
Orchestranion module start services in docker containers, examine and send configuraton to the front service.
Includes microserivice framework for easy develop simple services and easy expose by https through front.
More at project documentation
    """,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://github.com/rockstat/band-framework',
    include_package_data=True,
    install_requires=[
        'pyyaml<4', 'inflection', 'jinja2', 'python-dotenv',
        'requests', 
        'asyncio', 'uvloop', 'aiohttp<4', 'aioredis', 'aiojobs', 
        'aiodocker', 'aiofiles', 'async_lru', 'aiocron>=1.3,<2'
        'simplech',
        'jsonrpcserver==3.5.6', 'jsonrpcclient==2.6.0', 
        'prodict', 'pydantic', 'ujson', 'arrow', 
        'structlog', 'colorama', 'python-json-logger', 'coloredlogs'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={  # Optional
        'Homepage': 'https://rock.st',
        'Docs': 'https://rock.st/docs'
    })
