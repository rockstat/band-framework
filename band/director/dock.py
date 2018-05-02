from pathlib import Path
import docker
# from aiofiles import os
import os
from prodict import Prodict

from .. import logger

BASE_IMG_TMPL = 'rst/{}'
USER_IMG_TMPL = 'user/srv-{}'
SHORT_FIEL_LIST = []

LINBAND = 'inband'
LPORTS = 'ports'
LDELIM = ':'


def pack_ports(plist):
    return LDELIM.join([str(p) for p in plist])


def unpack_ports(pstr):
    return [int(p) for p in pstr.split(LDELIM)] if bool(pstr) else []


def short_info(container):
    return {key: getattr(container, key) for key in ['short_id', 'name', 'status', 'labels']}


def def_labels(alloc_ports=None):
    d = Prodict(inband='inband')
    if alloc_ports:
        d.ports = pack_ports(alloc_ports)
    return d


print(def_labels())


class Comment(Prodict):
    user_id: int
    comment: str
    date: str


class Labels(dict):
    @property
    def marked(self):
        return bool(self.get(LINBAND, False))

    def mark(self):
        self[LINBAND] = 'yes'
        return self

    @property
    def ports(self):
        pstr = self.get(LPORTS, None)
        return [int(p) for p in pstr.split(LDELIM)] if bool(pstr) else []

    @ports.setter
    def ports(self, plist):
        self[LPORTS] = LDELIM.join([str(p) for p in plist])

    def __getattr__(self, attr):
        return self.get(attr)


class Dock():
    """
    Docker api found at https://docs.docker.com/engine/api/v1.24/#31-containers
    """

    def __init__(self, bind_addr, images_path, default_image_path, container_env, **kwargs):

        self.dc = docker.from_env()
        self.initial_ports = list(range(8900, 8999))
        self.available_ports = list(self.initial_ports)

        self.bind_addr = bind_addr
        self.default_image_path = default_image_path
        self.container_env = container_env

        self.images_path = Path(images_path).resolve().as_posix()
        self.inspect_containers()

    def inspect_containers(self):
        containers = self.containers().values()

        for container in containers:
            self.inspect_container(container)

    def inspect_container(self, container):
        logger.info(f'inspecting container {container.name}')
        lbs = Prodict.from_dict(container.labels)
        for port in unpack_ports(lbs.ports):
            self.allocate_port(port)

    def containers(self):
        containers = self.dc.containers.list(all=True,
                                             filters={'label': LINBAND})
        return {c.name: c for c in containers}

    def containers_list(self):
        return list([short_info(c) for c in self.containers().values()])

    def get(self, name):
        return self.containers().items().get(name, None)

    def allocate_port(self, port=None):
        if port:
            if port in self.available_ports:
                logger.info(f"port {port} excluded")
                self.available_ports.remove(port)
            else:
                logger.info(f"hohoho smth wrong {port}: {type(port)}")
        else:
            port = self.available_ports.pop()
            logger.info(f"allocated port {port}")

        return port

    def remove_container(self, name):
        self.stop_container(name)

        cns = self.containers()

        if name in list(cns.keys()):
            logger.info("removing container {}".format(name))
            cns[name].remove()

        return True

    def stop_container(self, name):
        containers = self.containers()

        if name in list(containers.keys()):
            containers[name].stop()
            logger.info(f"stopping container {name}")
            return True

    def ping(self, name):
        return 'not implemented'

    def container_config(self, ports={}, alloc_ports=[], name='untitled'):
        return Prodict.from_dict({
            'name': name,
            'hostname': name,
            'ports': ports,
            'labels': def_labels(alloc_ports=alloc_ports),
            'environment': self.container_env,
            'detach': True,
            'auto_remove': True
        })

    def build_image(self, base, name):

        params = Prodict.from_dict({
            'path': self.default_image_path,
            'tag': USER_IMG_TMPL.format(name),
            'labels': def_labels()
        })
        logger.info(f"building service image {params.tag} from {params.path}")

        img, _ = self.dc.images.build(**params)
        return img

    def run_container(self, name, params):

        self.remove_container(name)

        logger.info("building image for {}".format(name))

        img = self.build_image(self.images_path, name)
        attrs = Prodict.from_dict(img.attrs)

        ports = {p: (self.bind_addr, self.allocate_port(),)
                 for p in attrs.Config.ExposedPorts or {}}
        alloc = [p[1] for p in ports.values()]

        params = self.container_config(
            name=name, ports=ports, alloc_ports=alloc)

        print(params)

        logger.info(f"starting container {name}. ports: {params.ports}")
        c = self.dc.containers.run(img.tags[0], **params)

        logger.info(f'started container {c.name} [{c.short_id}]')
        return short_info(c)
