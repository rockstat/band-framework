import asyncio
import uvloop
from aiohttp import web
import aiodocker
from aiohttp_utils import Response, routing, negotiation
import webargs
from webargs.aiohttpparser import use_args

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

# docs: https://docs.aiohttp.org/en/stable/
# docs: http://aiodocker.readthedocs.io/en/latest/
# docs: https://github.com/sloria/aiohttp_utils
# docs: https://webargs.readthedocs.io/en/latest
# docs: https://docker-py.readthedocs.io/en/stable/
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
    return Response({'items': items})


@use_args({'name': webargs.fields.Str(location='match_info', required=True)})
async def create_container(request, args):
    container = await docker.containers.run(config, name=args['name'])
    return Response({'container': container_to_json(container)})


app = web.Application()
negotiation.setup(
    app, renderers={
        'application/json': negotiation.render_json
    }
)

app.add_routes([
    web.get('/list', list_containers),
    web.get('/create/{name}', create_container)
])
# ])


web.run_app(app, host='127.0.0.1', port=8008)
