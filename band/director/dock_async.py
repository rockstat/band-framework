from pathlib import Path
import aiofiles
import asyncio
from inflection import underscore
import aiodocker
import os
import re
from prodict import Prodict
import ujson
import subprocess
from pprint import pprint
from .. import logger

"""

links:
http://aiodocker.readthedocs.io/en/latest/
https://docs.docker.com/engine/api/v1.37/#operation/ContainerList
https://docs.docker.com/engine/api/v1.24/#31-containers
"""


def tar_image_cmd(path):
    return ['tar', '-C', path, '-c', '-X', '.dockerignore', '.']


def underdict(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            key = underscore(key)
            new_dict[key] = underdict(value)
        return new_dict
    # if hasattr(obj, '__iter__'):
    #     return [underdict(value) for value in obj]
    else:
        return obj


def inject_attrs(cont):
    attrs = underdict(cont._container)
    attrs['name'] = (
        attrs['name'] if 'name' in attrs else attrs['names'][0]).strip('/')
    attrs['short_id'] = attrs['id'][:12]
    if 'state' in attrs and 'status' in attrs['state']:
        attrs['status'] = attrs['state']['status']
    if 'config' in attrs and 'labels' in attrs['config']:
        attrs['labels'] = attrs['config']['labels']
    cont.attrs = Prodict.from_dict(attrs)
    return cont


def pack_ports(plist=[]):
    return ':'.join([str(p) for p in plist])


def unpack_ports(pstr):
    return pstr and [int(p) for p in pstr.split(':')] or []


def def_labels(a_ports=[]):
    return Prodict(inband='inband', ports=pack_ports(a_ports))


def short_info(container):
    if hasattr(container, 'attrs'):
        inject_attrs(container)
    ca = container.attrs
    dic = Prodict.from_dict({key: getattr(container.attrs, key)
                             for key in ['short_id', 'name', 'status']})
    dic.ports = []
    if 'labels' in ca:
        if 'ports' in ca.labels:
            dic.ports = unpack_ports(ca.labels.ports)
    return dic


def image_name(name):
    return f'rst/service-{name}'


class Dock():
    """
    """

    def __init__(self, bind_addr, network, def_srv_img_path, def_srv_img_name, base_image_path, base_image_name, container_env, **kwargs):
        self.dc = aiodocker.Docker()
        self.initial_ports = list(range(8900, 8999))
        self.available_ports = list(self.initial_ports)
        self.bind_addr = bind_addr
        self.network = network
        self.base_image_path = Path(base_image_path).resolve().as_posix()
        self.base_image_name = base_image_name
        self.container_env = container_env
        self.def_srv_img_path = Path(def_srv_img_path).resolve().as_posix()
        self.def_srv_img_name = def_srv_img_name

    async def inspect_containers(self):
        conts = await self.containers()
        for cont in conts.values():
            await self.inspect_container(cont)
        return [short_info(cont) for cont in conts.values()]

    async def inspect_container(self, cont):
        logger.info(f"inspecting container {cont.attrs.name}")
        lbs = cont.attrs.labels
        for port in lbs.ports and unpack_ports(lbs.ports) or []:
            logger.info(f' -> {lbs.inband} port:{port}')
            self.allocate_port(port)

    async def conts_list(self):
        conts = await self.containers()
        return [short_info(cont) for cont in conts.values()]

    async def get(self, name):
        conts = await self.containers()
        return conts.get(name, None)

    async def containers(self):
        filters = ujson.dumps({
            'label': ['inband=inband']
        })
        conts = await self.dc.containers.list(all=True, filters=filters)
        for cont in conts:
            await cont.show()
        return {(cont.attrs.name): inject_attrs(cont) for cont in conts}

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
            logger.info(f"stopping container {name}")
            await conts[name].stop()
            return True

    async def restart_container(self, name):
        conts = await self.containers()
        if name in list(conts.keys()):
            logger.info(f"restarting container {name}")
            await conts[name].restart()
            return True

    async def create_image(self, name, path):
        img_id = None

        with subprocess.Popen(tar_image_cmd(path), stdout=subprocess.PIPE) as proc:
            img_params = Prodict.from_dict({
                'fileobj': proc.stdout,
                'encoding': 'identity',
                'tag': name,
                'labels': def_labels(),
                'stream': True
            })

            logger.info(
                f"building image {img_params} from {path}")
            async for chunk in await self.dc.images.build(**img_params):
                if isinstance(chunk, dict):
                    logger.debug(chunk)
                    if 'aux' in chunk:
                        img_id = underdict(chunk['aux'])
                else:
                    logger.debug('chunk: %s %s', type(chunk), chunk)
            logger.info('image created %s', img_id)

        img = await self.dc.images.get(name)
        return Prodict.from_dict(underdict(img))

    async def run_container(self, name, params):

        # build custom images
        if False:
            img_name = f'rst/service-{name}'
            img_path = ''
        else:
            # rebuild base image
            await self.create_image(self.base_image_name, self.base_image_path)
            # params for service image
            img_name = self.def_srv_img_name
            img_path = self.def_srv_img_path
        
        img = await self.create_image(img_name, img_path)

        ports = {port: [{'HostIp': self.bind_addr, 'HostPort': str(self.allocate_port())}]
                 for port in img.container_config.exposed_ports.keys() or {}}
        a_ports = [port[0]['HostPort'] for port in ports.values()]

        env = {'NAME': name}
        env.update(self.container_env)

        config = Prodict.from_dict({
            'Image': img.id,
            'Hostname': name,
            'Cmd': name,
            'Ports': ports,
            'Labels': def_labels(a_ports=a_ports),
            'Env': [f"{k}={v}" for k, v in env.items()],
            'StopSignal': 'SIGTERM',
            'HostConfig': {
                'RestartPolicy': {
                    'Name': 'unless-stopped'
                },
                'PortBindings': ports,
                'NetworkMode': self.network
            }
        })
        
        print(config)

        logger.info(f"starting container {name}. ports: {config.Ports}")
        c = await self.dc.containers.create_or_replace(name, config)
        await c.start()
        await c.show()
        c = inject_attrs(c)
        logger.info(f'started container {c.attrs.name} [{c.attrs.id}]')
        return short_info(c)
