from collections import defaultdict, namedtuple
import http.client
from urllib.parse import urlencode, urlparse
import requests
import random
import sys
import os
import json

DEF_HOST = 'localhost'
DEF_PORT = '8123'
DEF_DB = 'default'


class ChConnOpts(namedtuple('ChConnOpts', 'host port db user password')):
    __slots__ = ()
    @property
    def url(self):
        return f"http://{self.host}:{self.port}"
    @property
    def query(self):
        qd = {'database': self.db}
        if self.user or self.password:
            qd['user'] = self.user
            qd['password'] = self.password
        return qd

class ClickHouse:

    def __init__(self, host=None, port=None, db=None, user=None, password=None, session_id=None, use_env=True):
        """
        
        """
        dsn = os.getenv('CLICKHOUSE_DSN', None)

        if dsn is not None and use_env == True and host is None and port is None:
            u = urlparse(dsn)
            self.chc = ChConnOpts(
                host=u.hostname,
                port=u.port or DEF_PORT,
                db=u.path.strip('/') or DEF_DB,
                user=u.user,
                password=u.password)
        else:
            self.chc = ChConnOpts(
                host=host or DEF_HOST,
                port=port or DEF_PORT,
                db=db or DEF_DB,
                user=user,
                password=password)

        self.base_url = self.chc.url
        self.buffer = defaultdict(str)
        self.buffer_i = defaultdict(int)
        self.session_id = session_id
        self.buffer_limit = 1000

    def flush_all(self):
        for k in self.buffer:
            self.flush(k)

    def get_params(self, query):
        params = {'query': query}
        params.update(self.chc.query)

        if self.session_id is not None:
            params['session_id'] = self.session_id
        return params

    def flush(self, table):

        self.ch_insert(table, self.buffer[table])
        self.buffer[table] = ''
        self.buffer_i[table] = 0

    def push(self, table, doc, jsonDump=True):

        try:
            if jsonDump == True:
                doc = json.dumps(doc, ensure_ascii=False)

        except Exception as e:

            print("Error:", sys.exc_info()[0])
            print('err: ', str(e))
            print('doc:', doc)
            raise e

        self.buffer[table] += doc + '\n'
        self.buffer_i[table] += 1

        if self.buffer_i[table] == self.buffer_limit:
            self.flush(table)

    def ch_insert(self, table, body):

        conn = http.client.HTTPConnection(self.base_url)
        query = 'INSERT INTO {table} FORMAT JSONEachRow'.format(table=table)
        url = "?" + urllib.parse.urlencode(self.get_params(query))
        conn.request("POST", url, body.encode())
        result = conn.getresponse()
        resp = result.read()

        if result.status != 200:
            print(resp)
            raise Exception('ClickHouse error:' + result.reason)

    def post_raw(self, table, data):

        conn = http.client.HTTPConnection(self.base_url)

        query = 'INSERT INTO {table} FORMAT JSONEachRow'.format(table=table)
        url = "?" + urllib.parse.urlencode(self.get_params(query))
        conn.request("POST", url, data)
        result = conn.getresponse()
        resp = result.read()

        if result.status != 200:
            print(resp)
            raise Exception('ClickHouse error:' + result.reason)

    def select(self, query):

        conn = http.client.HTTPConnection(self.base_url)
        params = "?" + urllib.parse.urlencode(self.get_params(query))
        conn.request("GET",  params)
        result = conn.getresponse()
        res = result.read()

        if result.status != 200:
            print(res)
            raise Exception('ClickHouse error:' + result.reason)
        return res

    def select_stream(self, query):

        r = requests.get('http://' + self.base_url,
                         params=self.get_params(query), stream=True)
        if r.status_code != requests.codes.ok:
            print(r.text)
            r.raise_for_status()
        return r

    def run(self, query):

        conn = http.client.HTTPConnection(self.base_url)
        url = "?" + urllib.parse.urlencode(self.get_params(query))
        conn.request("POST", url)
        result = conn.getresponse()
        res = result.read()

        if result.status != 200:
            print(res)
            raise Exception('ClickHouse error:' + result.reason)

        return res
