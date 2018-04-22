from flask import Flask, request, jsonify, make_response
import docker
import time

import consul
import consul.std

import docker
client = docker.from_env()

app = Flask(__name__)
STATUS_OPERATING = 1


app.config.update(
    DEBUG=True,
    JSON_AS_ASCII=False,
    MAX_CONTENT_LENGTH=1024
)


@app.route('/')
def hello_world():
    return jsonify({'status': STATUS_OPERATING, 'ts': time.time()})


@app.route('/register/<name>')
def register(name):
    c = consul.Consul()
    res = c.agent.service.register(name)
    return jsonify({'result': res, 'ts': time.time()})


@app.route('/services')
def services():
    c = consul.Consul()
    res = c.agent.services()
    print(res)
    return jsonify(res)


@app.route('/containers')
def containers():
    res = []
    for c in client.containers.list():
        res.append({
            'name': c.name, 'image': c.image.tags.pop()
            # c.attrs
        })
    return jsonify(res)


@app.route('/container/<name>')
def container(name):
    item = client.containers.list()
    return 'Container %s' % name


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' and request.form['username'] and request.form['password']:
        return jsonify({'result': 200})
    return jsonify({})


@app.errorhandler(404)
def not_found(error):
    resp = make_response(jsonify({'result': 404}), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

