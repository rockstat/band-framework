import asyncio
import aiodocker



config = {
    "Cmd": ["/bin/ls"],
    "Image": "alpine:latest",
    "AttachStdin": False,
    "AttachStdout": False,
    "AttachStderr": False,
    "Tty": False,
    "OpenStdin": False,
}

docker = aiodocker.Docker()


def container_to_json(container):
    cont_obj = container._container
    names = cont_obj.get('Names')
    return {
        'id': cont_obj.get('Id'),
        'image': cont_obj.get('Image'),
        'name': names[0] if len(names) else '(none)'
    }

async def list_containers(request):
    items = [container_to_json(x) for x in await docker.containers.list(all=True)]
    return{'items': items}


async def create_container(request, args):
    container = await docker.containers.run(config, name=args['name'])
    return {'container': container_to_json(container)}

