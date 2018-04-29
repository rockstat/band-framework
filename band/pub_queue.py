import jsonrpcclient
from jsonrpcclient.async_client import AsyncClient
from jsonrpcclient.request import Request
from past.builtins import basestring
import asyncio
import ujson


class RedisWrapper:
    pass


class PreparedRequest(str):
    def __new__(cls, request):
        # Convert a list of strings, to one string
        if isinstance(request, list) and all(isinstance(i, basestring) for i in
                                             request):
            request = '[{}]'.format(', '.join(request))
        # Convert a json-serializable object (dict or list) to a string
        if not isinstance(request, basestring):
            request = ujson.dumps(request)
        # Should end up with a string
        assert isinstance(request, basestring)
        return str.__new__(cls, request)

    def __init__(self, request):
        super(PreparedRequest, self).__init__()
        #: Extra details used in log entry, can be set by clients in
        #: prepare_request
        self.log_extra = None
        self.log_format = None



class PubQueue(AsyncClient):
    def __init__(self, endpoint='none', service='any'):
        super(PubQueue, self).__init__(endpoint)
        self.service = service
        self.pending = {}
        self.queue = asyncio.Queue()
        self.timeout = 5

    async def dispatch(self, msg):
        if 'result' in msg and 'id' in msg and msg['id'] in self.pending:
            self.pending[msg['id']].set_result(msg)

    async def get(self):
        item = await self.queue.get()
        self.queue.task_done()
        return item

    def request(self, destination, method_name, *args, **kwargs):
        req = Request(':'.join([destination, method_name, self.service]), *args, **kwargs)
        return self.send(req, destination=destination, request_id=req['id'])

    async def send(self, request, **kwargs):
        request = PreparedRequest(request)
        self.prepare_request(request, **kwargs)
        self.log_request(request, request.log_extra, request.log_format)
        return await self.send_message(request, **kwargs)

    async def put(self, dest, data):
        await self.queue.put((dest, data,))

    async def send_message(self, request, **kwargs):
        id = kwargs['request_id']
        dest = kwargs['destination']
        # Outbound msgs queeue
        await self.put(dest, request.encode())
        # Waiting for response
        self.pending[id] = asyncio.Future()
        await asyncio.wait_for(self.pending[id], timeout=self.timeout)
        # Retunrning result
        result = self.pending[id].result()
        del self.pending[id]
        return self.process_response(result)

