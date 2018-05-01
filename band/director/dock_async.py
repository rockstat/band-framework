import asyncio
import aiodocker

# docs: http://aiodocker.readthedocs.io/en/latest/
# docs: https://docs.docker.com/engine/api/v1.37/#operation/ContainerList

# @use_args({'name': fields.Str(required=True)})
# @use_args({'name': fields.Str(missing='World')})
# @use_args({'name': fields.Str(location='match_info', missing='World')})

# await docker.close()


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

