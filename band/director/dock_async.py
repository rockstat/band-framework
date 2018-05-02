from pathlib import Path
# import docker
import aiofiles
import asyncio
from inflection import underscore
import aiodocker
import os
import re
from prodict import Prodict
from box import Box
import ujson

from .. import logger

"""

links:
http://aiodocker.readthedocs.io/en/latest/
https://docs.docker.com/engine/api/v1.37/#operation/ContainerList
https://docs.docker.com/engine/api/v1.24/#31-containers
"""

config = {
    "Cmd": ["/bin/ls"],
    "Image": "alpine:latest",
    "AttachStdin": False,
    "AttachStdout": False,
    "AttachStderr": False,
    "Tty": False,
    "OpenStdin": False,
}

def recursive_key_map(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            key = underscore(key)
            new_dict[key] = recursive_key_map(value)
        return new_dict
    # if hasattr(obj, '__iter__'):
    #     return [recursive_key_map(value) for value in obj]
    else:
        return obj

def inject_attrs(cont):
    
    attrs = recursive_key_map(cont._container)
    attrs['name'] = attrs['names'][0].strip('/')
    attrs['short_id'] = attrs['id'][:12]
    cont.attrs = Prodict.from_dict(attrs)
    return cont


def pack_ports(plist=[]):
    return ':'.join([str(p) for p in plist])


def unpack_ports(pstr):
    return pstr and [int(p) for p in pstr.split(':')] or []


def def_labels(a_ports=[]):
    return Box(inband='inband', ports=pack_ports(a_ports))


def short_info(container):
    return {key: getattr(container.attrs, key)
            for key in ['short_id', 'name', 'status', 'labels']}


def image_name(name):
    return f'rst/service-{name}'


class Dock():
    """

    """

    def __init__(self, bind_addr, images_path, default_image_path, container_env, **kwargs):

        self.dc = aiodocker.Docker()
        self.initial_ports = list(range(8900, 8999))
        self.available_ports = list(self.initial_ports)

        self.bind_addr = bind_addr
        self.default_image_path = Path(default_image_path).resolve().as_posix()
        self.container_env = container_env

        self.images_path = Path(images_path).resolve().as_posix()

    async def inspect_containers(self):
        conts = await self.containers()
        print(conts)
        for cont in conts.values():
            await self.inspect_container(cont)

    async def inspect_container(self, cont):
        logger.info(f"inspecting container {cont.attrs.name}")
        lbs = cont.attrs.labels
        for port in lbs.ports and unpack_ports(lbs.ports) or []:
            logger.info(f' -> {lbs.inband} port:{port}')
            self.allocate_port(port)

    async def conts_list(self):
        conts = await self.containers()
        print(conts)
        return [short_info(cont) for cont in conts.values()]

    async def containers(self):
        filters = ujson.dumps({
            'label': ['inband=inband']
        })
        print(filters)
        conts = await self.dc.containers.list(all=True, filters=filters)
        return {(cont.attrs.name): inject_attrs(cont) for cont in conts}

    async def get(self, name):
        return (await self.containers()).get(name, None)

    def allocate_port(self, port=None):
        if port and port in self.available_ports:
            self.available_ports.remove(port)
            return port
        return self.available_ports.pop()

    async def remove_container(self, name):
        await self.stop_container(name)
        conts = await self.containers()
        if name in list(conts.keys()):
            logger.info(f"removing container {name}")
            await conts[name].delete()

        return True

    async def stop_container(self, name):
        conts = await self.containers()

        if name in list(conts.keys()):
            await conts[name].stop()
            logger.info(f"stopping container {name}")
            return True


    async def run_container(self, name, params):



        
        file = f'{self.default_image_path}/band.tar'

        with open(file, mode='rb') as f:
            # contents = await f.read()

            logger.info(f"building image for {name}")
            img_params = Prodict.from_dict({
                'fileobj': f,
                'encoding': 'utf-8',
                # 'remote': f"file://{self.default_image_path}",
                # 'remote': f'{self.default_image_path}/Dockerfile',
                'tag': image_name('async-py'),
                'labels': def_labels()
            })
            logger.info(f"building service image {img_params.tag} from {img_params.path_dockerfile}")
            img = await self.dc.images.build(**img_params)

        
        

        attrs = Prodict.from_dict(img)

        ports = {port: (self.bind_addr, self.allocate_port(),)
                 for port in attrs.Config.ExposedPorts.keys() or {}}
        a_ports = [port[1] for port in ports.values()]

        config = Box({
            'Image': attrs.tags[0],
            'Hostname': name,
            'Ports': ports,
            'Labels': def_labels(a_ports=a_ports),
            'Env': self.container_env,
            'StopSignal': 'SIGTERM',  # def sigterm
            'HostConfig': {
                'RestartPolicy': 'unless-stopped'
            }
        })
        print(config)

        logger.info(f"starting container {name}. ports: {config.ports}")
        c = await self.dc.containers.create_or_replace(name, config)

        logger.info(f'started container {c.name} [{c.short_id}]')
        return short_info(c)
